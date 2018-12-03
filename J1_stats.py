class Team(object):
    
    
    def __init__(self, team):
        url = f"http://www.football-lab.jp/{team}/match"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        
        table = soup.body.find("table", class_="statsTbl10")
        
        #カラム名取得
        col_names = []
        for th in table.thead.tr.find_all("th"):
            if th.text=="":
                col_names.append("HA")
                continue
            col_names.append(th.text)
        
        #データ取得
        data = []
        for match_data in table.tbody.find_all("tr"):
            for td in match_data.find_all("td"):
                text = td.text.replace("\u3000", " ")
                data.append(text)

        n_columns = len(col_names)
        
        self.df = pd.DataFrame(np.array(data).reshape(-1, n_columns), columns=col_names)
        self.df.index = self.df["節"]
        del self.df["節"]
        self.df["勝敗"] = self.df["スコア"].apply(self.score_to_result)
        self.df["得点"] = self.df["スコア"].apply(self.goals)
        self.df["失点"] = self.df["スコア"].apply(self.concedes)
        self.df["得失"] = self.df["スコア"].apply(self.plus_minus)
        
        self.df["シュート成功率"] =  self.df["シュート成功率"].apply(self.from_percentage)
        self.df["チャンス構築率"] = self.df["チャンス構築率"].apply(self.from_percentage)
        self.df["支配率"] = self.df["支配率"].apply(self.from_percentage)
        self.df["シュート"] = self.df["シュート"].apply(int)
        self.df["観客数"] = self.df["観客数"].apply(lambda n: int(n.replace(",", "")))
        
        self.df["天候"] = self.df["天候"].apply(self.meteo)
        
    def meteo(self, met):
        if len(met)==1:
            return met
        if "雨" in met:
            return "雨"
        if "晴" in met or met=="屋内":
            return "晴"
        print(met)
        return "不明"
        
    def from_percentage(self, ratio):
        return float(ratio[:-1])/100
    
    def to_csv(self):
        self.df.to_csv(f"{FOOT_OUTPUT}/team_results/{year}_{team}.csv", encoding="cp932", index=False)
        
    def fetch(self):
        return self.df
    
    def goals(self, score):
        return int(score.split("-")[0])
    
    def concedes(self, score):
        return int(score.split("-")[1])
    
    def plus_minus(self, score):
        return int(score.split("-")[0]) - int(score.split("-")[1])
    
    def score_to_result(self, score):
        goals = score.split("-")[0]
        concedes = score.split("-")[1]
        if goals > concedes:
            return "W"
        if goals < concedes:
            return "L"
        if goals == concedes:
            return "D"
        return None
def rank_to_class(rank):
    r = int(rank)
    if r<=4:
        return 0
    if r<=11:
        return 1
    if r<=18:
        return 2
def main():
	rank = pd.read_csv(f"{FOOT_PATH}data/j1_ranking_2018.csv")
	rank["class_"] = rank["順位"].apply(rank_to_class)
	rank["相手"] = rank["チーム略"]
	del rank["チーム略"]
	

	#2017年のJ1チームとフットボールラボ上での表記
	j1_2017 = {"鳥栖": "tosu", "柏": "kasw", "大宮": "omiy", "FC東京": "fctk", "甲府": "kofu",
			   "川崎Ｆ": "ka-f","広島": "hiro", "浦和": "uraw", "神戸": "kobe", "新潟": "niig",
			   "横浜FM": "y-fm", "仙台": "send", "清水": "shim", "C大阪": "c-os", "鹿島": "kasm",
			   "磐田": "iwat", "札幌": "sapp", "G大阪": "g-os"}

	j1_2018 = {"鳥栖": "tosu", "柏": "kasw", "FC東京": "fctk", "川崎Ｆ": "ka-f","広島": "hiro",
			   "浦和": "uraw", "神戸": "kobe", "横浜FM": "y-fm", "仙台": "send", "清水": "shim", 
			   "C大阪": "c-os", "鹿島": "kasm", "磐田": "iwat", "札幌": "sapp", "G大阪": "g-os",
			   "長崎":"ngsk", "名古屋": "nago", "湘南": "shon"}

	year = 2018
	team_jp = "長崎"

	if year==2017:
		team = j1_2017[team_jp]
	else:
		team = j1_2018[team_jp]

	stats = Team(team)
	df = pd.merge(stats.fetch(), rank, on="相手")
