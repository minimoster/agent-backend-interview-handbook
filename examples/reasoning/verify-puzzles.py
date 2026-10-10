"""Original checks for explicitly stated, idealized puzzle rules."""
from collections import deque
from itertools import combinations
import json
import math

def bfs(capacities, start, goal, refill):
    queue=deque([start]); previous={start:None}; action={}
    while queue:
        s=queue.popleft()
        if goal(s):
            steps=[]
            while previous[s] is not None:
                steps.append({'action':action[s],'state':s});s=previous[s]
            return [{'action':'start','state':start}]+steps[::-1]
        candidates=[]
        for i in range(len(s)):
            if refill:
                t=list(s);t[i]=capacities[i];candidates.append((tuple(t),f'fill {i+1}'))
                t=list(s);t[i]=0;candidates.append((tuple(t),f'empty {i+1}'))
            for j in range(len(s)):
                if i==j:continue
                q=min(s[i],capacities[j]-s[j]);t=list(s);t[i]-=q;t[j]+=q
                candidates.append((tuple(t),f'pour {i+1} -> {j+1}'))
        for t,a in candidates:
            if t not in previous:
                previous[t]=s;action[t]=a;queue.append(t)
    raise AssertionError('no path')

paths={
 '5_6_to_3':bfs((5,6),(0,0),lambda s:3 in s,True),
 '10_7_3_split':bfs((10,7,3),(10,0,0),lambda s:s==(5,5,0),False),
 '7_11_to_2':bfs((7,11),(0,0),lambda s:2 in s,True),
}
# Hourglass state: minutes of sand remaining in the upper chamber.
remaining=[4,7];capacity=[4,7];timeline=[];time=0
for target,flips in [(4,[0]),(7,[1]),(8,[1]),(9,[])]:
    elapsed=target-time
    remaining=[max(0,x-elapsed) for x in remaining]
    before=remaining[:]
    for i in flips:remaining[i]=capacity[i]-remaining[i]
    timeline.append({'time':target,'before_flip':before,'flip':[i+1 for i in flips],'after_flip':remaining[:]})
    time=target
assert remaining[1]==0

# Verify the 25-horse seven-race schedule over many deterministic total orders.
import random
rng=random.Random(20261009)
for _ in range(10000):
    speed=list(range(25));rng.shuffle(speed)
    groups=[sorted(speed[i:i+5]) for i in range(0,25,5)]
    groups.sort(key=lambda g:g[0])
    A,B,C,D,E=groups
    result=[A[0]]+sorted([A[1],A[2],B[0],B[1],C[0]])[:2]
    assert result==[0,1,2]

# Verify an AT MOST 11 race schedule for 64 horses/8 lanes/top 4.
# This is not a lower-bound proof of optimality.
for _ in range(10000):
    speed=list(range(64));rng.shuffle(speed)
    groups=[sorted(speed[i:i+8]) for i in range(0,64,8)]
    groups.sort(key=lambda g:g[0])
    A,B,C,D=groups[:4]
    finalists=sorted([A[1],A[2],B[0],B[1],B[2],C[0],C[1],D[0]])[:3]
    # A4 can enter top 4 only if A2 and A3 occupy the first two places here.
    if set(finalists[:2])==set(A[1:3]):
        finalists=sorted(finalists+[A[3]])[:3]
    result=[A[0]]+finalists
    assert result==[0,1,2,3]

def pirates(n,strict):
    previous=[]
    for k in range(1,n+1):
        votes=k//2+1 if strict else math.ceil(k/2)
        needed=votes-1
        costs=sorted(((0 if coins is None else coins+1,i) for i,coins in enumerate(previous)))
        selected=costs[:needed]
        price=sum(c for c,_ in selected)
        if len(selected)<needed or price>100:
            previous=[None]+previous
        else:
            allocation=[100-price]+[0]*(k-1)
            for c,i in selected:allocation[i+1]=c
            previous=allocation
    return previous
assert pirates(5,False)==[98,0,1,0,1]
assert pirates(5,True)==[97,0,1,2,0]

empty,total=20,20
while empty>=2:
    new=empty//2;total+=new;empty=empty%2+new
assert (total,empty)==(39,1)
assert {sum(c) for r in range(4) for c in combinations([1,2,4],r)}==set(range(8))
print(json.dumps({'scope':'Idealized stated rules only; simulations are not optimality proofs',
'jug_paths':paths,'hourglass_timeline':timeline,'horse_schedules_random_cases_each':10000,
'pirate_half_passes':pirates(5,False),'pirate_strict_majority':pirates(5,True),
'bottles_no_borrow':total,'gold_subsets':'0..7 all represented'},ensure_ascii=False,indent=2))
