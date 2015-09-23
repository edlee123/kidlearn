def spe_promo_window_not_sync(self):
        stepSuccess = self.stepMax

        first = -1
        for ii in range(self.nval):
            if self.bandval[ii] != 0:
                first = ii
                break

        last = self.nval-1
        for ii in range(self.nval-1,-1,-1):
            if self.bandval[ii] != 0:
                last = ii
                break

        max_usable_val = [self.success_rate(-stepSuccess,val =[x]) for x in self.active_bandits() if self.len_success()[x] >= self.stepMax and x not in self.use_to_active]

        if len(max_usable_val) > 0:
            imax = self.active_bandits()[np.argmax(max_usable_val)]
            max_succrate_active = self.success_rate(-self.stepMax, val = [imax])

            if max_succrate_active > self.upZPDval and last+1 < len(self.bandval):# and imax not in self.use_to_active: # and first < len(self.bandval) - 3:
                self.bandval[last+1] = min(self.bandval[last],self.bandval[last-1])/2
                self.use_to_active.append(imax)

        max_usable_val = [self.success_rate(-self.stepUpdate,val =[x]) for x in self.active_bandits() if self.len_success()[x] >= self.stepUpdate]
        
        if len(max_usable_val) > 0:
            imax = self.active_bandits()[np.argmax(max_usable_val)]
            max_succrate_active = self.success_rate(-self.stepUpdate, val = [imax])

            if max_succrate_active > self.deactZPDval and imax != last: # and len(self.active_bandits()) > 1  and first < len(self.bandval) - 3:
                self.bandval[imax] = 0
            #for i in range(len(self.success)):
                #    if mean(self.success[i][-self.stepMax:]) > self.deactZPDval and len(self.success[i]) > self.stepMax and i != last:
                #        self.bandval[i] = 0