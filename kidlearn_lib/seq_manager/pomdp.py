#-*- coding: utf-8 -*-
## POMDP
## 2014 BCLEMENT
import numpy as np
import numpy.matlib as npmat
import copy
import scipy.sparse as sparse

#np.random.seed(20)

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
    
    def __init__(self, params = None,  params_file = "seq_test_1", directory = "params_files"):
        self._Ps = 0.05
        self._Pg = 0.05

        self._Pt = np.array([[.3, 0, 0, 0, 0],
                             [ 0,.1, 0, 0, 0],
                             [ 0, 0,.2, 0, 0],
                             [ 0, 0, 0,.3, 0],
                             [ 0, 0, 0, 0,.25]])
        self._nA = 5
        self._nS = pow(2,self._nA)
        self._nZ = 2
        self._gamma = 0.99
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

        tmp = np.cumsum(T[S,:])
        Snew = np.where(tmp >= np.random.rand())[0][0]
        
        # Simulate new observation

        tmp = np.cumsum(O[Snew,:])
        Znew = np.where(tmp >= np.random.rand())[0][0]

        # Update belief 

        if B != None:
            Bnew = self.blfUpdt(B,A,Znew)

        return Snew, Rnew, Znew, Bnew

    def reward(self,state,action):
        return self._R[state,action]


    def blfUpdt(self,B,A,Z):
        T = self._P[A]
        O = self._O[A][:,Z]

        # Update belief
        Bnew = np.dot(B , T ) * O.T

        if sum(Bnew) == 0:
            Bnew = O.T

        Bnew = Bnew/sum(Bnew)

        return Bnew

    def traj(self,V,b0,s0,nsteps):
        b = b0
        S = s0
        D = [["S","R","Z","a","b"]]
        for ii in range(nsteps):
            a = self.sample(V, b)
            if isinstance(a,int):
                a = [a]
            a = a[np.random.randint(len(a))]
            [S, R, Z, b] = self.step(S, a, b) # we should not know the true state, check if code allows that
            D.append([S,R,Z,a])
            #print D
            if(self._AS[S]==1):
                break
        return D

    # Expe code adaptation

    def init_to_traj(self):
        self.current_belief = self.s0

    def update(self,act, corsol = True, nbFault = 0, *args, **kwargs):
        self.current_belief = self.blfUpdt(self.current_belief,act,corsol)

    def sample(self,V,b,isQMDP = False):
        # If Q-MDP choose action directly
        if isQMDP:
            Q = V * b.T
            A = greedy('samp',Q)

        # else: Build Q-matrix
        else:
            Q = np.zeros( self._nA)
            for a in range(self._nA):
                b = np.matrix(b)

                # Compute updated beliefs for current action and all observations

                Vaux = (b * self._P[a]).T

                Vaux = np.multiply(npmat.repmat(Vaux,1,self._nZ) , self._O[a])
                Vaux = V * Vaux

                Vmax = np.amax(Vaux, 0)[0]
                
                # Compute observation probabilities and multiply

                Q[a] = (b * np.matrix(self._R[:, a]).T).item(0,0) + self._gamma * np.sum(Vmax)
            #print Q
            A = greedy('prob',Q)

        return A



#########################################################################################

def greedy(mode,U):
    Idx = np.argmax(U,axis = 0)

    if mode == 'samp':
        a = Idx[np.ceil(len(Idx) * np.random.rand())]
    elif mode == 'prob':
        a = Idx
    
    if isinstance(a,int):
        p = 1
    else:
        p = 1/len(a);

    return a


def perseus_init():
        echo = 1
        max_iterr = 10000
        eps = 1e-9
        return echo,max_iterr,eps

def perseus(pomdp = None, D = None):
    # Input (inputs marked with * are mandatory): 
    # . POMDP* (POMDP Model: struct(nS, nA, nZ, {P}, {O}, r, Gamma, s0, b0))
    # . D      (Set of sampled beliefs)
    # 
    # Output (outputs marked with * are mandatory): 
    # . V    (alpha-vector set)

    echo,max_iterr,eps = perseus_init()
    
    # Parse arguments
    pomdp = pomdp or POMDP()
    D = D or pomdp.sampleBeliefs()
    
    #print D[[1,2],:]
    
    quit = 0
    iterr = 1

    # Initialize V set
  #  print "R %s" % pomdp._R
  #  print "rmin %s"  % pomdp._R.min(axis = 0)

    #V = np.ndarray(min(pomdp._R.min(axis = 0)) * np.ones((pomdp._nS)) / (1 - pomdp._gamma))
    V = np.matrix(min(pomdp._R.min(axis = 0)) * np.ones((pomdp._nS)) / (1 - pomdp._gamma))
  #  print "V %s" %  V
    
    while quit == 0:

        #return perseusBackup(pomdp, V, D)
        #print "iterr %s" % iterr
        Vnew = perseusBackup(pomdp, V, D)
        
        Vaux = D * Vnew.T
        vNew = np.amax(Vaux,axis = 1)
        #print "vNew %s" % vNew
        Vaux = D * V.T
        vOld = np.amax(Vaux,axis = 1)
        #print "vOld %s" % vOld
        
        Err = np.max(np.abs(vOld - vNew))
        #print Err
        #raw_input()

        #if echo:
        #    print "Error at iterration %s : %s" % (iterr, Err)

        
        if Err < eps or iterr == max_iterr:
            print "iterr %s" % iterr 
            print "err %s" % Err
            quit = 1
        else :
            iterr = iterr + 1

        V = Vnew
    return pomdp,V,D

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
    # . max_iterr
    # . eps
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
    # M. Spaan, N. Vlassis. Perseus: Randomized point-based value iterration for
    # POMDPs. In "Journal of Artificial Intelligence Research", vol. 24, pp.
    # 195-220, 2005.
    echo,max_iterr,eps = perseus_init()

    quit = 0
    iterr = 1

    # 1a) Initialize new alpha-vector set

    Vnew = []
    Dqueue = D
    while quit == 0:
        nB = np.size(Dqueue, 0)
        nV = np.size(V, 0)
        # 2a) Sample belief from Dqueue

        tmp = int(np.ceil(nB * np.random.rand())-1)
        b = Dqueue[tmp, :]
        indTable = range(tmp)+range(tmp+1,nB)
        try:
            Dqueue = Dqueue[indTable,:]
        except:
            Dqueue = sparse.csr_matrix((0,pomdp._nS))
        # 2b) Compute a = backup(b)

        g = np.zeros((pomdp._nS, pomdp._nA))
    
        for a in range(0,pomdp._nA):
            
            # Compute updated beliefs for current action and all observations

            bnew = (b * pomdp._P[a]).T

            bnew = np.multiply(npmat.repmat(bnew,1,pomdp._nZ) , pomdp._O[a])
        
            # Multiply by alpha-vectors and maximize

            idx = V * bnew
  #          print "idx %s" % idx
            idx = np.argmax(idx, axis = 0)
 #           print "V %s" % V
            Vupd = V[idx,:][0]
            #Vupd = np.repeat(V, idx.shape[1], axis=0)

#            print "Vupd %s" % Vupd 
            
            # Compute observation probabilities and multiply
   #         print pomdp._O[a].shape 
    #        print Vupd.T.shape
            OxVupd = np.sum(np.multiply(pomdp._O[a], Vupd.T), 1)
            #print "OxVupd %s" % OxVupd
            #raw_input()
            #print np.matrix(pomdp._R[:, a]).T.shape
            #print np.asarray(np.matrix(pomdp._R[:, a]).T + pomdp._gamma * pomdp._P[a] * OxVupd)[:,0]
            #print g[:, a]
            g[:, a] = np.asarray(np.matrix(pomdp._R[:, a]).T + pomdp._gamma * pomdp._P[a] * OxVupd)[:,0]
            #print "g shape %s" % str(g.shape)

        # To make g and V same dimensional
        g = g.T
    
        # Compute new vector to add to new basis
        
        #print "g %s" %  str(g.shape)
        #print type(g)
        tmp = b * g.T
        #print "tmp g %s" %  str(tmp.shape)
        vNew = np.amax(tmp, 1)[0]
        kNew = np.argmax(tmp, 1)[0]
        #print "kNew %s" % kNew
        
        #V = np.asarray(V)
        #print "V %s" %  str(V.shape)
        #print type(V)
        tmp = b * np.asarray(V).T
        #print "tmp V %s" %  str(tmp.shape)
        vOld = np.amax(tmp, 1)[0]
        kOld = np.argmax(tmp, 1)[0]
        #print "kOld %s" % kOld

        if vNew >= vOld:
            aNew = g[kNew, :]
            #print "an new %s" % str(aNew.shape)
        else :
            aNew = np.asarray(V)[kOld, :]
            #print "an old %s" % str(aNew.shape)
        #print aNew
         
        # Add new vector to basis

        if np.size(Vnew) == 0:
            tmp = 0
        else:
            #tmp = aNew(ones(size(Vnew, 1), 1),:) == Vnew
            tmp = np.equal(npmat.repmat(aNew,len(Vnew),1), Vnew)
            tmp = np.sum(tmp.astype(float), axis =1)
            #print tmp 

        if np.all(tmp != pomdp._nS):
            Vnew.append(aNew)
        
        # Recompute Dqueue
        
        Vaux = Dqueue * np.matrix(V).T
        vOld = np.amax(Vaux, 1)
        
        #print "Vnew %s" % Vnew
        #print "Vnew shape %s " % str(np.matrix(Vnew).T.shape)
        #print "Dqueue shape %s " % str(Dqueue.shape)

        Vaux = Dqueue * np.matrix(Vnew).T
        vNew = np.amax(Vaux, 1)
        tmp = np.asarray(np.less_equal(vNew, vOld).astype(float).T)[0]
        idx = [x for x  in range(len(tmp)) if tmp[x] == 1]

        try :
            Dqueue = Dqueue[idx,:]
        except: 
            Dqueue = sparse.csr_matrix((0,pomdp._nS))

        
        if Dqueue.size == 0 or iterr == max_iterr:
            quit = 1
        else:
            iterr = iterr + 1

    return np.matrix(Vnew)



