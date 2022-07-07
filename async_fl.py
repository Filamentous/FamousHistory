from operator import itemgetter
import math
from riotwatcher import LolWatcher
import time, json


class Famous_list():
    """
    View readme.md
    """
    def __init__(self) -> None: 
        self.MAX_REQUESTS_SEC = 20
        self.MAX_REQUESTS_2MIN = 100
        self.RIOT_JITTER = 0.25 # probably unneccessary but its funny
        self.OPS_COUNTER = 0
        self.SCRIPT_START = time.perf_counter()


    def _get_history(self, lolusername:str, countreq:int=0, region:str='na1'):    
        """
        lolusername: summonername, username to check against processed list
        countreq: number of games to check (default=0 is all games)
        region: the region which to retrieve summoner information from
        """
        try:
            if countreq == 0:
                countreq=9999
            index = 0
            matches = []
            lol_watcher = LolWatcher('')
            first = time.perf_counter()
            #print("get summoner")
            user = lol_watcher.summoner.by_name(region, lolusername)
            self.OPS_COUNTER = self.OPS_COUNTER + 1
            puuid = user['puuid']
            for _ in range(self.MAX_REQUESTS_SEC-2):
                #print("get matches")
                diff = time.perf_counter() - self.SCRIPT_START
                allowance = (math.floor(diff/120)+1)*self.MAX_REQUESTS_2MIN
                if allowance<=self.OPS_COUNTER:
                    print("MUST WAIT OUT CD for:", 120-diff)
                    time.sleep(120 - diff)
                ret = lol_watcher.match.matchlist_by_puuid(region, puuid, start=index, count=100)
                self.OPS_COUNTER= self.OPS_COUNTER + 1
                print(self.OPS_COUNTER)
                if len(ret) == 0:
                    return matches
                matches.extend(ret)
                index+=100
                if index >= countreq:
                    return matches
            second = time.perf_counter()
            if 1-(second-first)>0:
                time.sleep((1-(second-first))+self.RIOT_JITTER)
            for _ in range(3):#do rest of ops per 2min
                rmatch, index = self._op_second(index, puuid, region)
                matches.extend(rmatch)
            third = time.perf_counter()
            if((third - first) <120):
                time.sleep(120 - (third-first)+self.RIOT_JITTER)   
            while(index<countreq):
                if (countreq-index>500):
                    rmatch, index = self._op_2min(index, puuid, region)
                    matches.extend(rmatch)
                else:
                    ret, index = self._op_2minosleep(index, puuid, region)
                    matches.extend(rmatch)
                if index == -1:
                    return matches
            return matches
        except:
            return None

    def _op_second(self, index:int, puuid, region:str):
        matches = []
        first = time.perf_counter()
        print("op_Second")
        lol_watcher = LolWatcher('RGAPI-b8ec1d1b-6426-4039-a921-02eeeacecdde')
        for _ in range(self.MAX_REQUESTS_SEC-1):
            print("get matches")
            allowance = (((self.SCRIPT_START - time.perf_counter()-((self.SCRIPT_START - time.perf_counter()%120))/120)+1)*self.MAX_REQUESTS_2MIN)
            print(allowance)
            ret = lol_watcher.match.matchlist_by_puuid(region, puuid, start=index, count=100)
            self.OPS_COUNTER= self.OPS_COUNTER + 1
            if len(ret) == 0:
                index = -1
                return matches
            matches.append(ret)
            index+=100
        second = time.perf_counter()
        if (second-first)>1:
            time.sleep((second-first)-1+self.RIOT_JITTER)
        return matches, index

    def _op_2min(self, index:int, puuid, region:str):
        #assumes new cycle
        first = time.perf_counter()
        for _ in range(4):
            matches, index = self._op_second(index, matches, puuid, region)
        second = time.perf_counter()
        if((second - first) <120):
            time.sleep(120 - (second-first)+self.RIOT_JITTER)
        return matches, index

    def _op_2minosleep(self, index:int, puuid, region:str):
        #assumes new cycle
        for _ in range(4):
            matches, index = self._op_second(index, puuid, region)
        return matches, index

    def _make_fp_chunk(self, fp:str, acc:list):
        #acc : [{accname:gameid}, ...]
        if len(acc)==0:
            print("REMOVE", acc, fp)
            return "\""+fp+"\":"+"\" \""
        out = "\""+fp+"\":{" # header
        for x in acc[:-1]:#may need to be -2
            out+="\n"+x+","
        out+="\n"+acc[-1]+"\n}" #foot
        out.replace("\'", "\"")
        return out


    def check_json(self, name:str='league.json'):
        """
        checks a json file that all summoner names exist, very useful for larger data sets
        name: name of the file
        """
        f = open(name, 'r')
        data = json.load(f)
        for f in data:
            acc_list = []
            un_csv = str(data[f])
            un_list = un_csv.split(',')
            for b in un_list:
                history = self._get_history(b, 80)
                if history is None:
                    print("EMPTY HISTORY")
                    break
                if len(history) == 0:
                    print("EMPTY HISTORY")
                    break
                out = history[0]
                for x in history[1:]:
                    out+=','+x
                    acc_list.append("\""+x+"\":\""+out+"\"")
                    #print(acc_hist_list)
                    for t in acc_list:
                        t.replace("\'", "")
                self._make_fp_chunk(f, acc_list)
                print(b, "exists")


    def process_json(self, name:str='league.json', out_name:str='fpgameid.json'):
        """
        Processes a list of summoner names and creates a json formatted to be read by check history
        name: file name to be processed
        out_name: file name of the proccessed list (does overwrite the file)
        """
        f = open(name, 'r')
        data = json.load(f)
        n = open(out_name, 'w')
        n.write("{")
        for fp in data:
            acc_hist_list = []
            un_csv = str(data[fp])
            un_list = un_csv.split(',')
            for alt in un_list:
                history = self._get_history(alt, 0)
                if history is None:
                    print("EMPTY HISTORY")
                    break
                if len(history) == 0:
                    print("EMPTY HISTORY")
                    break
                out = history[0]
                for x in history[1:]:
                    out+=','+x
                acc_hist_list.append("\""+alt+"\":\""+out+"\"")
                #print(acc_hist_list)
                for t in acc_hist_list:
                    t.replace("\'", "")
            ret = self._make_fp_chunk(fp, acc_hist_list)
            print(ret)
            n.write(ret + ",\n")
        n.write("}")
        n.close()

    def check_user(self, user:str, namejson:str='fpgameid1.json'):
        """
        Checks user against specified output file processed json
        user: summoner name, to check
        """
        f = open(namejson, 'r')
        data = json.load(f)
        hit_list = []
        user_history=self._get_history(user,0)
        if user_history == None:
            return []
        for user_game in user_history:
            for fp in data:
                for alt in data[fp]:
                    #print(alt)
                    if alt == " ":
                        break
                    game_csv = str(data[fp][alt])
                    game_list = game_csv.split(",")
                    for fp_game in game_list:
                        #print(fp_game)
                        if fp_game == user_game and alt !=user:
                            dis = str(fp) +' AS '+ str(alt)
                            hit_list.append((fp_game,dis))
        hit_list.sort(key=itemgetter(1))
        return hit_list

if __name__ == '__main__':
    fl_inter = Famous_list()
    #fl_inter.check_json('league.json')
    #fl_inter.process_json('league.json')
    #hits = fl_inter.check_user("SUMMONERNAME")
    #print(hits)
