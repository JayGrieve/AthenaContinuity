import Sprob
import athena
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from multivariate_hypergeom_sample import multivhyper
import copy
import ast

class Athena_Continuity:
    
    def __init__(self, vote_dist : dict, round_sched: int):
        
        self.vote_dist = vote_dist
        self.round_sched = round_sched
    
    def run(self, risk_limit: float) -> bool:
        
        # Type check risk limit
        if type(risk_limit) is not float:
            raise TypeError("Risk limit must be float")
        if risk_limit >= 1.0 or risk_limit <= 0.0:
            raise ValueError("Risk limit must be between 0 and 1.0")

        # Create distribution object to sample from ballots in election
        ballots = multivhyper(self.vote_dist)
        
        #Variables to keep track of the reported winner
        winner = max(self.vote_dist, key=self.vote_dist.get)
        windex = max(self.vote_dist.values())
        #Keeps track of the pairwise audits that have passed the risk limit
        self.can_stop = dict.fromkeys([x for x in self.vote_dist if x!= winner],False)
        #Keeps track of the p values for each round for each pairwise audit
        self.p_values =  dict.fromkeys([x for x in self.vote_dist if x!= winner])
        for p in self.p_values:
            self.p_values[p] = []
        #Stores the athena objects for each pairwise audit
        self.audits = copy.deepcopy(self.vote_dist)
        del self.audits[winner]
    
        self.round_sizes = dict.fromkeys(self.audits,[])
        for a in self.audits:
            self.audits[a] = athena.Athena(windex + self.audits[a],windex,copy.deepcopy(self.round_sched),risk_limit,True)
        # Run audit until stop or full recount
        current_round = 0
        self.prev = dict.fromkeys(self.vote_dist,0)
        while current_round <len(self.round_sched):
            #print("CURRENT ROUND",current_round)
            if all(self.can_stop.values()):
                break
            # Get a sample of ballots
            if current_round == 0:
                sample = ballots.sample(self.round_sched[current_round])
            else:
                sample = ballots.sample(self.round_sched[current_round] - self.round_sched[current_round-1])
                
            
            # Add ballots in new sample to running count of votes in audit
            fixed = {}
            for i,value in enumerate(ballots.types):
                fixed[value] = sample[i] + self.prev[value]
            
            sample = fixed   
            self.prev = copy.deepcopy(sample)
            
            for a in self.audits:
                #Sets the sample size for the audit to the artificial sample size from the draws
                getattr(self.audits[a],'round_sched')[current_round] = sample[winner] + sample[a]
                
                self.audits[a].compute_audit()
                #If it passes k_min
                if sample[winner] >= self.audits[a].k_min_sched[current_round] and self.audits[a].alpha > risk_limit/1000:  
                    #print("REDUCING ALPHA: ", a, 'KMIN: ',self.audits[a].k_min_sched[current_round], 'KDRAWN: ',sample[winner])
                    self.can_stop[a] = True
                    
                    #add the lowest p value this current iteration passed (this round)
                    self.p_values[a].append(copy.deepcopy(self.audits[a].risk_sched[current_round]))

                   
                    #get a new risk limit from k_min = k_drawn+1
                    temp_sched = self.audits[a].k_min_sched
                    temp_sched[current_round] = sample[winner]+1
                    
                    result = Sprob.Sprob(self.audits[a].N,self.audits[a].Ha_tally,self.audits[a].round_sched,temp_sched)
                    result.compute_risk()
                    

                    result = result.risk_sched[current_round]
                    #self.p_values[a].append(result)
                    self.audits[a] = athena.Athena(self.audits[a].N,self.audits[a].Ha_tally,self.audits[a].round_sched,result,True)
                
                else:
                    #else, just record the pvalue of the round
                    temp_sched = self.audits[a].k_min_sched
                    temp_sched[current_round] = sample[winner]                    
                    result = Sprob.Sprob(self.audits[a].N,self.audits[a].Ha_tally,self.audits[a].round_sched,temp_sched)
                    result.compute_risk()
                    result = result.risk_sched[current_round]
                    self.p_values[a].append(copy.deepcopy(result))
                
                
                
               

                    
                    
            
            
            current_round+=1
            
        
        
        return False




'''
bernie = []
warren = []
yang = []
kanye = []

for i in range(250):
    dist = {'biden':10000,'bernie':9250,'warren':9000,'yang':8500,'kanye':2000}
    round_sched = [1000,2000,3000,4000,5000,6000,7000,8000]
    test = Athena_Continuity(dist,round_sched)
    test.run(.05)
    temp_bernie = {'passed': test.can_stop['bernie'],'p_values':test.p_values['bernie']}
    temp_bernie['min'] = None if len(test.p_values['bernie']) == 0 else min(test.p_values['bernie'])
    
    temp_warren = {'passed': test.can_stop['warren'],'p_values':test.p_values['warren']}
    temp_warren['min'] = None if len(test.p_values['warren']) == 0 else min(test.p_values['warren'])

    temp_yang = {'passed': test.can_stop['yang'],'p_values':test.p_values['yang']}
    temp_yang['min'] = None if len(test.p_values['yang']) == 0 else min(test.p_values['yang'])
    
    temp_kanye = {'passed': test.can_stop['kanye'],'p_values':test.p_values['kanye']}
    temp_kanye['min'] = None if len(test.p_values['kanye']) == 0 else min(test.p_values['kanye'])

    bernie.append(temp_bernie)
    warren.append(temp_warren)
    yang.append(temp_yang)
    kanye.append(temp_kanye)
    if i%25 == 0:
        print(round(i/250 * 100,2),'%')

pd.DataFrame(warren).to_csv('warren.csv',index = None)
pd.DataFrame(bernie).to_csv('bernie.csv',index = None)
pd.DataFrame(yang).to_csv('yang.csv',index = None)
pd.DataFrame(kanye).to_csv('kanye.csv',index = None)


w = pd.read_csv('warren.csv')
y = pd.read_csv('yang.csv')
b = pd.read_csv('bernie.csv')
k = pd.read_csv('kanye.csv')


       
y_2 = y[y['passed'] == True]
w_2 = w[w['passed'] == True]
b_2 = b[b['passed'] == True]
k_2 = k[k['passed'] == True]

w[w['passed'] == True].count()
b[b['passed'] == True].count()

vals = [.05,.04,.03,.02,.01,0]
res = []
for i in range(len(vals)-1):
    res.append((y_2[y_2['min'] < vals[i]].count() - y_2[y_2['min'] < vals[i+1]].count()).iloc[0])
print(sum(res))
res = []
for i in range(len(vals)-1):
    res.append((b_2[b_2['min'] < vals[i]].count() - b_2[b_2['min'] < vals[i+1]].count()).iloc[0])
print(sum(res))
res = []
for i in range(len(vals)-1):
    res.append((w_2[w_2['min'] < vals[i]].count() - w_2[w_2['min'] < vals[i+1]].count()).iloc[0])
print(sum(res))
res = []
for i in range(len(vals)-1):
    res.append((k_2[k_2['min'] < vals[i]].count() - k_2[k_2['min'] < vals[i+1]].count()).iloc[0])    

print(sum(res))

z = w['min'][w['passed'] == True]
z = b['min'][b['passed'] == True]
z = y['min'][y['passed'] == True]
z = k['min'][k['passed'] == True]

plt.scatter(z,z.index)
plt.xlim(0, 0.06)
plt.title('Biden vs. Kanye')
plt.xlabel('Risk at end')
plt.ylabel('Trial Number')
z[z<.04].count()


temp = k.to_dict('records')
temp1 = {'Round 1':[],'Round 2':[],'Round 3':[],'Round 4':[],'Round 5':[],'Round 6':[],'Round 7':[],'Round 8':[]}
for t in temp:
    t['p_values'] = ast.literal_eval(t['p_values'])
    if len(t['p_values'])>8:
        t['p_values'] = t['p_values'][:-1]
    elif len(t['p_values'])<8:
        t['p_values'][len(t['p_values']):8] = [t['p_values'][-1] for x in range(8-len(t['p_values']))]
    t['p_values'] = list(np.minimum.accumulate(t['p_values']))
    for i,p in enumerate(t['p_values']):
        temp1['Round ' + str(i+1)].append(p)

o = pd.DataFrame(temp1)

z = o.boxplot()
z.set_ylabel("Risk (Minimum p-value)")
title = 'Biden vs. Kanye'
plt.title(title)
plt.yscale("log")

'''
