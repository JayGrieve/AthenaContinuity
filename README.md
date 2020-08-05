# AthenaContinuity

# The Problem

Incorporating the risk of ballot draws in all rounds in multicandidate audits where some pairwise canidates pass the risk limit in the first round 

# Motivating Example


In multicandidate elections, the audits are preformed as pairwise audits of the candidates. Consider an audit with three candidates Biden, Warren, and Sanders. Assume that in the first round, the audit for (Biden, Sanders) passes the risk limit but the audit for (Biden, Warren) does not, and thus the whole audit must continue to the next round. Ballots for all candidates will continue to be drawn, and thus we have extra information concerning (Biden, Sanders) that could potentially be used to report an even lower risk limit than achieved in round 1.

# Proposed Solution

### Proceeding to next round:
In order to proceed to the next round, increase k_min to, equivelently k_drawn + 1, resulting in a lower risk limit.

### Not passing following rounds:

There is a case where after artificially increasing k_min, the audit does not pass in the next rounds, or rounds after that. As long as one or more of the pairwise audits are still needing to be continued, this is fine. But in the case where in some round > 1, all other pairwise audits meet the stopping condition, but the artificially continued pairwise audits do not, for each of the artificially continued audits, simply select the minimum p value passed across all rounds.

### Continuing to pass k_min:


In the case where in some round > 1, the ballots drawn are again greater then k_min, a recompution of the whole audit is needed considering the risk limit implied by the incrementing of k_min in that round. 



# Experimental Results

In order to test the above solution, I implemented the changes using the Athena audit method. I ran the audit on a four candidate election with candiates Biden, Sanders, Warren, Yang, and Kanye with 10000, 9250, 9000, 8500, and 2000 reported votes respectively. The risk limit of the audit was .05. For ballot drawing, 1000 ballots were drawn each round for, a maximum of 8 rounds, sampled from a multivariate hypergeometric distribution. 

 
|           |        |            | Risk of Audit at Completion |         |  |         |         |
|-----------|--------|------------|:------------------------------:|---------|----------------------|---------|---------|
| Candidate | Margin | #Completed | .05-.04                        | .04-.03 | .03-.02              | .02-.01 | .01-.00 |
| Sanders   | .039   | 164        | 138                            | 9       | 6                    | 7       | 4       |
| Warren    | .052   | 229        | 82                             | 13      | 19                   | 37      | 74      |
| Yang      | .081   | 249        | 10                             | 2       | 7                    | 9       | 221     |
| Kanye     | .66    | 250        | 0                              | 0       | 0                    | 0       | 250     |


## Analysis
The above table describes the risk of the audits who completed within the 8 round maximum of the simulation. As you can see, with wider margins the ultimate risk of the audit can be greatly reduced through this method. One thing is important to note, why does Sanders have signifigantly less reduction in risk than Warren when there margins are not very different? This is because Sanders has the lowest margin meaning the Sanders audit is, in most cases, the audit which neccesitates that the whole audit continue.


![](https://raw.githubusercontent.com/JayGrieve/AthenaContinuity/master/sanders_lp.png?token=AKRZ4FODVJBM53ZRST34HT27FMIR4)
![](https://raw.githubusercontent.com/JayGrieve/AthenaContinuity/master/warren_lp.png?token=AKRZ4FNVJ6NHFXQSCCE565S7FMIVG)
![](https://raw.githubusercontent.com/JayGrieve/AthenaContinuity/master/yang_lp.png?token=AKRZ4FINPSOYITGXLXFXU7C7FMIWM)
![](https://raw.githubusercontent.com/JayGrieve/AthenaContinuity/master/kanye_lp.png?token=AKRZ4FONONAJMNA77W3CBR27FMIXO)


## Analysis

The graphs above display the benefits of using this method to lower the risk of audits. It can be seen that the extra information attained by continuing the audit greatly lowers the overall risk for all of the other candidates.





 


