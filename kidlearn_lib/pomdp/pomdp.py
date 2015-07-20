#-*- coding: utf-8 -*-
## POMDP
## 2014 BCLEMENT
import numpy as np
import numpy.matlib as npmat
import copy
import scipy.sparse as sparse

np.random.seed(20)

class POMDP(object):
#  POMDP* (POMDP Model: struct(nS     , nA       ,nZ, {P}, {O}, r, Gamma, s0, b0))
#  nS :nrStates       - (1 x 1) number of states
# # states         - (nrStates x X) chars, name of each state *)
#  nA : nrActions      - (1 x 1) number of actions
# # actions        - (nrActions x X) chars, name of each action *)
#  nZ : nrObservations - (1 x 1) number of observations
# # observations   - (nrObservations x X) chars, name of each
#                   observation *)
#  gamma          - (1 x 1) discount factor
#  r? : values         - (1 x X) chars, 'reward' or 'cost'
#  sO : start          - (1 x nrStates) start distribution *)

#  r? reward3        - (nrStates x nrStates x nrActions)
#                       s'         s           a     R(s',s,a)
#  {O} observation    - (nrStates x nrActions x nrObserva
#                       s'         a           o     P(o|s',a)
#  {P} transition     - (nrStates x nrStates x nrActions)
#                       s'         s           a     P(s'|s,a)
#  nB*    (Number of belief points to be sampled)
    
    def __init__(self):
        self._Ps = 0.05
        self._Pg = 0.05

        self._Pt = np.array([[.5, 0, 0, 0, 0],
                             [ 0,.8, 0, 0, 0],
                             [ 0, 0,.7, 0, 0],
                             [.4, 0, 0,.6, 0],
                             [ 0, 0, 0, 0,.9]])
        self._nA = 5
        self._nS = pow(2,self._nA)
        self._nZ = 2
        self._Gamma = 0.99
        #self._b0 = ones(1,self._nS)/self._nS;
        self._s0 = np.zeros(self._nS)
        self._s0[0] = 1
        self._AS = np.zeros(self._nS)
        self._AS[-1] = 1
        self._R = np.array([np.zeros(5) for x in range(self._nS)],dtype = 'float128')
        self._P = np.array([[np.zeros(self._nS) for x in range(self._nS)]for x in range(self._nA)],dtype = 'float128')
        self._O = np.array([[np.zeros(2) for x in range(self._nS)] for x in range(self._nA)],dtype = 'float128')
        self.construct_pomdp()

        self._nB = 1350

        #D = self.sampleBeliefs()

    def construct_pomdp(self):
        for ii in range(0,self._nS):
            str_ss = np.binary_repr(ii,5)
            ss = np.array([int(x) for x in str_ss])
            for aa in range(self._nA):
                nss = copy.copy(ss)
                self._R[ii] = [sum(ss)]*5
                if ss[aa] == 1:
                    iss = int(str_ss,2)
                    #no forgetting
                    self._P[aa][ii][iss] = 1
                    self._O[aa][ii] = [1-self._Ps, self._Ps]
                else:
                    nss[aa] = 1
                    iss = int(''.join([str(x) for x in nss]),2)
                    aux = np.dot(ss, self._Pt[aa,:][np.newaxis].T) + self._Pt[aa,aa]
                    self._P[aa][ii][iss] = aux
                    self._P[aa][ii][ii] = 1-aux
                    self._O[aa][ii] = [self._Pg, 1-self._Pg]

    def sampleBeliefs(self,nB = None):

        # Input (inputs marked with * are mandatory):
        # . POMDP* (POMDP Model: struct(nS, nA, nZ, {P}, {O}, r, gamma, s0, b0))
        # . nB*    (Number of belief points to be sampled)
        #
        # Output (outputs marked with * are mandatory):
        # . D (Data-set containing nB beliefs)
        #
        # Init parameters:
        #
        # . None
        #    # Initialize state
        nB = nB or self._nB
        
        S = self.initS()

        # Initialize belief

        if hasattr(self, '_s0'):
            b = self._s0
        else:
            b = np.ones((0,self._nS))/self._nS

        # Initialize belief dataset

        #D = np.zeros((nB,self._nS))
        D = sparse.csr_matrix((nB,self._nS))
        D[0,:] = b

        i = 1
        k = 0

        while i <= nB and k < 100 :
            # Sample action
            A = np.ceil((self._nA) * np.random.rand())-1
        
        # Simulate transition
            
            S, Rnew, Znew, Bnew = self.step(S, A, b)

            if self._AS[S] == 1:
                b = np.ones((self._nS))/self._nS
                S = self.initS()
            else:
                b = Bnew

            
             # Compute distance to exis
            Dist = np.sum(np.power(npmat.repmat(b,i,1) - D[0:i,:],2),axis = 1)

            #if np.min(Dist) >= 1e-5 :
            if np.matrix.min(Dist) >= 1e-5 :
                i = i+1
                k = 0
                D[i-1, :] = b
            else :
                k = k+1
                S = self.initS()
                b = np.ones((self._nS))/self._nS

        D = D[0:i,:]

        return D

    def initS(self):
        if hasattr(self, '_s0'):
            S = self._s0
            if len(S) > 1:
                TMP = np.cumsum(S)
                S = np.where(TMP >= np.random.rand())[0][0]
        else:
            S = np.ceil(self._nS * np.random.rand())-1

        return S

    def step(self,S, A, B = None):
        # function [Snew, Rnew, Znew, Bnew] = POMDPstep(POMDP, S, A, B)
        #
        # Input (inputs marked with * are mandatory): 
        # . POMDP* (POMDP Model: struct(nS, nA, nZ, {P}, {O}, R, gamma, s0, b0))
        # . S*     (Current POMDP state)
        # . A*     (Current action)
        # . B      (Current believ)
        # 
        # Output (outputs marked with * are mandatory): 
        # . Snew (New state)
        # . Rnew (New reward)
        # . Znew (New observation)
        # . Bnew (New belief)
        #
        # Init parameters:
        #
        # . None
        T = self._P[A]
        O = self._O[A]

        #Compute reward

        Rnew = self._R[S,A]

        # Simalte new state

        TMP = np.cumsum(T[S,:])
        Snew = np.where(TMP >= np.random.rand())[0][0]

        # Simulate new observation

        TMP = np.cumsum(O[Snew,:])
        Znew = np.where(TMP >= np.random.rand())[0][0]

        # Update belief 

        if B != None:
            Bnew = self.blfUpdt(B,A,Znew)

        return Snew, Rnew, Znew, Bnew

    def blfUpdt(self,B,A,Z):
        T = self._P[A]
        O = self._O[A][:,Z]

        # Update belief
        Bnew = np.dot(B , T ) * O.T

        if sum(Bnew) == 0:
            Bnew = O.T

        Bnew = Bnew/sum(Bnew)

        return Bnew

#########################################################################################

def perseus_init():
        ECHO = 1
        MAX_ITER = 1000
        EPS = 1e-9
        return ECHO,MAX_ITER,EPS

def perseus(pomdp = None, D = None):
    # Input (inputs marked with * are mandatory): 
    # . POMDP* (POMDP Model: struct(nS, nA, nZ, {P}, {O}, r, Gamma, s0, b0))
    # . D      (Set of sampled beliefs)
    # 
    # Output (outputs marked with * are mandatory): 
    # . V    (alpha-vector set)

    ECHO,MAX_ITER,EPS = perseus_init()
    
    # Parse arguments
    pomdp = pomdp or POMDP()
    D = D or pomdp.sampleBeliefs()
    
    #print D[[1,2],:]
    
    Quit = 0
    Iter = 1

    # Initialize V set
    print "R %s" % pomdp._R
    print "rmin %s"  % pomdp._R.min(axis = 0)

    V = min(pomdp._R.min(axis = 0)) * np.ones((pomdp._nS)) / (1 - pomdp._Gamma)
    print "V %s" %  V
    
    while Quit == 0:

        return perseusBackup(pomdp, V, D)
        Vnew = perseusBackup(pomdp, V, D)
    
        Vaux = D * Vnew.T
        vNew = np.amax(Vaux,axis = 0)

        Vaux = D * V.T
        vOld = np.amax(Vaux,axis = 0)
        
        Err = full(max(np.abs(vOld - vNew)))

        #if ECHO:
        #    print "Error at iteration %s : %s" % (Iter, Err)

        
        if Err < EPS or Iter == MAX_ITER:
            Quit = 1
        else :
            Iter = Iter + 1
        
        V = Vnew

def perseusBackup(pomdp, V, D):
    # function [Vnew] = perseusBackup(POMDP, V, D)
    #
    # Input (inputs marked with * are mandatory): 
    # . POMDP* (POMDP Model: struct(nS, nA, nZ, {P}, {O}, r, gamma, s0, b0))
    # . V      (Set of alpha-vectors to be updated)
    # . D      (Belief dataset)
    # 
    # Output (outputs marked with * are mandatory): 
    # . Vnew   (Updated alpha-vector set)
    #
    # Init parameters:
    #
    # . MAX_ITER
    # . EPS
    # Perseus Backup:
    #
    # 1. Initialization
    #    a) Set V(n+1) = []
    #    b) Dqueue = D;
    #
    # 2. a) Sample a belief point b uniformly at random from Dqueue
    #    b) compute a = backup(b)
    # 
    # 3. a) if b.a >= V(n,b), 
    #          add a to V(n+1)
    #       else 
    #          add a' = argmax[ai] b.ai to V(n+1)
    # 
    # 4. Compute B' = {b in B : V(n+1,b) < Vn(b)}
    #
    # 5. if isempty(B') stop, else goto 2.
    #
    # References:
    #
    # M. Spaan, N. Vlassis. Perseus: Randomized point-based value iteration for
    # POMDPs. In "Journal of Artificial Intelligence Research", vol. 24, pp.
    # 195-220, 2005.
    ECHO,MAX_ITER,EPS = perseus_init()

    Quit = 0
    Iter = 1

    # 1a) Initialize new alpha-vector set

    Vnew = []
    Dqueue = D
    while Quit == 0:
        nB = np.size(Dqueue, 0)
        nV = np.size(V, 0)
        print "nV %s" % nV
        # 2a) Sample belief from Dqueue

        tmp = int(np.ceil(nB * np.random.rand())-1)
        b = Dqueue[tmp, :]
        indTable = range(tmp)+range(tmp+1,nB)
        
        Dqueue = Dqueue[indTable,:]
        
        # 2b) Compute a = backup(b)

        g = np.zeros((pomdp._nS, pomdp._nA))
    
        for a in range(0,pomdp._nA):
            
            # Compute updated beliefs for current action and all observations

            bnew = (b * pomdp._P[a]).T

            bnew = np.multiply(npmat.repmat(bnew,1,pomdp._nZ) , pomdp._O[a])
        
            # Multiply by alpha-vectors and maximize
            
            print V

            """
            # bug for NOW TO DO DEbugging 
            """
            
            Idx = V * bnew
            Idx = np.amax(Idx, 0)
            Vupd = V[Idx, :]

            # Compute observation probabilities and multiply
            
            OxVupd = np.sum(np.dot(pomdp._O[a], Vupd.T), 1)
            g[:, a] = pomdp._R[:, a] + pomdp._Gamma * pomdp._P[a] * OxVupd

            # To make g and V same dimensional
            g = g.T

        [vNew, kNew] = np.amax(b * g.T, 2)
        [vOld, kOld] = np.amax(b * V.T, 2)