# ToDo: add a list of valid languages and test against it


class Abbreviations(object):
    """Deliver a localized abbreviation for a Bible book given an English index or abbreviation. 

"""
    languages = []
    def __init__(self, language="en"):
        # index by 1
        self.language = language
        self.index_abbreviations = [None] + _biblebookabbreviations
        self.en_abbreviations = {data["en"]: data
                                 for data in _biblebookabbreviations}
        self.language_abbreviations = {data[self.language]: data
                                        for data in _biblebookabbreviations}

    def abbreviation_for_index(self, index, language):
        assert index > 1 and index <= 87, f"Invalid index: {index}"
        return self.index_abbreviations[index][language]

    def abbreviation_for_en(self, abbrev, language):
        assert abbrev in self.en_abbreviations, f"Invalid abbreviation: {abbrev}"
        return self.en_abbreviations[abbrev][language]

    def abbreviation_for_foreign_language(self, abbrev, language):
        assert abbrev in self.language_abbreviations, f"Invalid abbreviation: {abbrev}"
        return self.language_abbreviations[abbrev][language]
        
        
_biblebookabbreviations = [
{'index': '1', 'en': 'Ge', 'de': 'Gen', 'es': 'Gn', 'pt': 'Gn', 'ko': '창', 'zh-Hans': '创', 'zh-Hant': '創'},
{'index': '2', 'en': 'Ex', 'de': 'Ex', 'es': 'Éx', 'pt': 'Êx', 'ko': '출', 'zh-Hans': '出', 'zh-Hant': '出'},
{'index': '3', 'en': 'Le', 'de': 'Lev', 'es': 'Lv', 'pt': 'Lv', 'ko': '레', 'zh-Hans': '利', 'zh-Hant': '利'},
{'index': '4', 'en': 'Nu', 'de': 'Num', 'es': 'Nm', 'pt': 'Nm', 'ko': '민', 'zh-Hans': '民', 'zh-Hant': '民'},
{'index': '5', 'en': 'Dt', 'de': 'Dtn', 'es': 'Dt', 'pt': 'Dt', 'ko': '신', 'zh-Hans': '申', 'zh-Hant': '申'},
{'index': '6', 'en': 'Jos', 'de': 'Jos', 'es': 'Jos', 'pt': 'Js', 'ko': '수', 'zh-Hans': '书', 'zh-Hant': '書'},
{'index': '7', 'en': 'Jdg', 'de': 'Ri', 'es': 'Jue', 'pt': 'Jz', 'ko': '삿', 'zh-Hans': '士', 'zh-Hant': '士'},
{'index': '8', 'en': 'Ru', 'de': 'Ru', 'es': 'Rt', 'pt': 'Rt', 'ko': '룻', 'zh-Hans': '得', 'zh-Hant': '得'},
{'index': '9', 'en': '1 Sa', 'de': '1Sa', 'es': '1 Sm', 'pt': '1Sm', 'ko': '삼상', 'zh-Hans': '撒上', 'zh-Hant': '撒上'},
{'index': '10', 'en': '2 Sa', 'de': '2Sa', 'es': '2 Sm', 'pt': '2Sm', 'ko': '삼하', 'zh-Hans': '撒下', 'zh-Hant': '撒下'},
{'index': '11', 'en': '1 Ki', 'de': '1Kö', 'es': '1 Re', 'pt': '1Rs', 'ko': '왕상', 'zh-Hans': '王上', 'zh-Hant': '王上'},
{'index': '12', 'en': '2 Ki', 'de': '2Kö', 'es': '2 Re', 'pt': '2Rs', 'ko': '왕하', 'zh-Hans': '王下', 'zh-Hant': '王下'},
{'index': '13', 'en': '1 Ch', 'de': '1Chr', 'es': '1 Cr', 'pt': '1Cr', 'ko': '대상', 'zh-Hans': '代上', 'zh-Hant': '代上'},
{'index': '14', 'en': '2 Ch', 'de': '2Chr', 'es': '2 Cr', 'pt': '2Cr', 'ko': '대하', 'zh-Hans': '代下', 'zh-Hant': '代下'},
{'index': '15', 'en': 'Ezr', 'de': 'Esr', 'es': 'Esd', 'pt': 'Ed', 'ko': '스', 'zh-Hans': '拉', 'zh-Hant': '拉'},
{'index': '16', 'en': 'Ne', 'de': 'Neh', 'es': 'Neh', 'pt': 'Ne', 'ko': '느', 'zh-Hans': '尼', 'zh-Hant': '尼'},
{'index': '17', 'en': 'Es', 'de': 'Est', 'es': 'Est', 'pt': 'Et', 'ko': '에', 'zh-Hans': '斯', 'zh-Hant': '斯'},
{'index': '18', 'en': 'Job', 'de': 'Ij', 'es': 'Job', 'pt': 'Jó', 'ko': '욥', 'zh-Hans': '伯', 'zh-Hant': '伯'},
{'index': '19', 'en': 'Ps', 'de': 'Ps', 'es': 'Sal', 'pt': 'Sl', 'ko': '시', 'zh-Hans': 'Ps', 'zh-Hant': 'Ps'},
{'index': '20', 'en': 'Pr', 'de': 'Spr', 'es': 'Pr', 'pt': 'Pv', 'ko': '잠', 'zh-Hans': '箴', 'zh-Hant': '箴'},
{'index': '21', 'en': 'Ec', 'de': 'Koh', 'es': 'Ec', 'pt': 'Ec', 'ko': '전', 'zh-Hans': '传', 'zh-Hant': '傳'},
{'index': '22', 'en': 'So', 'de': 'Hld', 'es': 'Cnt', 'pt': 'Ct', 'ko': '아', 'zh-Hans': '歌', 'zh-Hant': '歌'},
{'index': '23', 'en': 'Is', 'de': 'Jes', 'es': 'Is', 'pt': 'Is', 'ko': '사', 'zh-Hans': '赛', 'zh-Hant': '賽'},
{'index': '24', 'en': 'Je', 'de': 'Jer', 'es': 'Jr', 'pt': 'Jr', 'ko': '렘', 'zh-Hans': '耶', 'zh-Hant': '耶'},
{'index': '25', 'en': 'La', 'de': 'Klgl', 'es': 'Lm', 'pt': 'Lm', 'ko': '애', 'zh-Hans': '哀', 'zh-Hant': '哀'},
{'index': '26', 'en': 'Eze', 'de': 'Ez', 'es': 'Ez', 'pt': 'Ez', 'ko': '겔', 'zh-Hans': '结', 'zh-Hant': '結'},
{'index': '27', 'en': 'Da', 'de': 'Dan', 'es': 'Dn', 'pt': 'Dn', 'ko': '단', 'zh-Hans': '但', 'zh-Hant': '但'},
{'index': '28', 'en': 'Ho', 'de': 'Hos', 'es': 'Os', 'pt': 'Os', 'ko': '호', 'zh-Hans': '何', 'zh-Hant': '何'},
{'index': '29', 'en': 'Joe', 'de': 'Joe', 'es': 'Jl', 'pt': 'Jl', 'ko': '욜', 'zh-Hans': '珥', 'zh-Hant': '珥'},
{'index': '30', 'en': 'Am', 'de': 'Am', 'es': 'Am', 'pt': 'Am', 'ko': '암', 'zh-Hans': '摩', 'zh-Hant': '摩'},
{'index': '31', 'en': 'Ob', 'de': 'Obd', 'es': 'Abd', 'pt': 'Ob', 'ko': '옵', 'zh-Hans': '俄', 'zh-Hant': '俄'},
{'index': '32', 'en': 'Jon', 'de': 'Jona', 'es': 'Jon', 'pt': 'Jn', 'ko': '욘', 'zh-Hans': '拿', 'zh-Hant': '拿'},
{'index': '33', 'en': 'Mic', 'de': 'Mi', 'es': 'Mi', 'pt': 'Mq', 'ko': '미', 'zh-Hans': '弥', 'zh-Hant': '彌'},
{'index': '34', 'en': 'Na', 'de': 'Nah', 'es': 'Nah', 'pt': 'Na', 'ko': '나', 'zh-Hans': '鸿', 'zh-Hant': '鴻'},
{'index': '35', 'en': 'Hab', 'de': 'Hab', 'es': 'Hab', 'pt': 'Hc', 'ko': '합', 'zh-Hans': '哈', 'zh-Hant': '哈'},
{'index': '36', 'en': 'Zep', 'de': 'Zef', 'es': 'Sof', 'pt': 'Sf', 'ko': '습', 'zh-Hans': '番', 'zh-Hant': '番'},
{'index': '37', 'en': 'Hag', 'de': 'Hag', 'es': 'Hag', 'pt': 'Ag', 'ko': '학', 'zh-Hans': '该', 'zh-Hant': '該'},
{'index': '38', 'en': 'Zec', 'de': 'Sach', 'es': 'Zac', 'pt': 'Zc', 'ko': '슥', 'zh-Hans': '亚', 'zh-Hant': '亞'},
{'index': '39', 'en': 'Mal', 'de': 'Mal', 'es': 'Mal', 'pt': 'Ml', 'ko': '말', 'zh-Hans': '玛', 'zh-Hant': '瑪'},
{'index': '40', 'en': 'Tob', 'de': 'Tob', 'es': 'Tob', 'pt': 'Tb', 'ko': '토비', 'zh-Hans': '多俾亚传', 'zh-Hant': '多俾'},
{'index': '41', 'en': 'Jdt', 'de': 'Jdt', 'es': 'Jdt', 'pt': 'Jt', 'ko': '유딧', 'zh-Hans': '犹滴传', 'zh-Hant': '友'},
{'index': '42', 'en': 'Gk Es', 'de': 'Greek Esther', 'es': 'Es Ad', 'pt': 'Et Gr', 'ko': '에스(외)', 'zh-Hans': 'Additions to Esther', 'zh-Hant': 'Additions to Esther'},
{'index': '43', 'en': 'Wis', 'de': 'Weish', 'es': 'Sab', 'pt': 'Sb', 'ko': '지혜', 'zh-Hans': '所罗门智训', 'zh-Hant': '智'},
{'index': '44', 'en': 'Sir', 'de': 'Sir', 'es': 'Eclo', 'pt': 'Eclo', 'ko': '집회', 'zh-Hans': '德训篇', 'zh-Hant': '德'},
{'index': '45', 'en': 'Bar', 'de': 'Bar', 'es': 'Bar', 'pt': 'Br', 'ko': '바룩', 'zh-Hans': '巴鲁书', 'zh-Hant': '巴'},
{'index': '46', 'en': 'Let Jer', 'de': 'BrJer', 'es': 'Car Jer', 'pt': 'Ca Je', 'ko': '렘의 편지', 'zh-Hans': '耶利米书信', 'zh-Hant': '耶利米書信'},
{'index': '47', 'en': 'Song Thr', 'de': 'GebAs', 'es': 'Or Az', 'pt': 'Oração de Azarias', 'ko': '세 아이의 노래', 'zh-Hans': 'Prayer of Azariah', 'zh-Hant': 'Prayer of Azariah'},
{'index': '48', 'en': 'Sus', 'de': 'Sus', 'es': 'Sus', 'pt': 'Sus', 'ko': '수산나', 'zh-Hans': 'Sus', 'zh-Hant': 'Sus'},
{'index': '49', 'en': 'Bel', 'de': 'Bel', 'es': 'Bel', 'pt': 'Bel', 'ko': '벨과 용', 'zh-Hans': '比勒與大龍', 'zh-Hant': '比勒與大龍'},
{'index': '50', 'en': '1 Mac', 'de': '1Ma', 'es': '1 Ma', 'pt': '1Ma', 'ko': '1마카', 'zh-Hans': '马加比壹书', 'zh-Hant': '馬加比壹書'},
{'index': '51', 'en': '2 Mac', 'de': '2Ma', 'es': '2 Ma', 'pt': '2Ma', 'ko': '2마카', 'zh-Hans': '马加比贰书', 'zh-Hant': '馬加比貳'},
{'index': '52', 'en': '1 Esd', 'de': '1Es', 'es': '1 Esd', 'pt': '1Ed', 'ko': '에스드라 1서', 'zh-Hans': '1 Esdras', 'zh-Hant': '1 Esdras'},
{'index': '53', 'en': 'Pr Man', 'de': 'GebMan', 'es': 'Or Man', 'pt': 'Oração de Manassés', 'ko': '므낫세의 기도', 'zh-Hans': 'Prayer of Manasseh', 'zh-Hant': 'Prayer of Manasseh'},
{'index': '54', 'en': 'Ps 151', 'de': 'Ps 151', 'es': 'Sal 151', 'pt': 'Sl 151', 'ko': '시 151', 'zh-Hans': '시 151', 'zh-Hant': '시 151'},
{'index': '55', 'en': '3 Mac', 'de': '3Ma', 'es': '3 Ma', 'pt': '3Ma', 'ko': '3마카', 'zh-Hans': '馬加比參書', 'zh-Hant': '馬加比三'},
{'index': '56', 'en': '2 Esd', 'de': '2Es', 'es': '2 Esd', 'pt': '2Ed', 'ko': '에스드라 2서', 'zh-Hans': '2 Esdras', 'zh-Hant': '2 Esdras'},
{'index': '57', 'en': '4 Mac', 'de': '4Ma', 'es': '4 Ma', 'pt': '4Ma', 'ko': '4마카', 'zh-Hans': '马加比肆書', 'zh-Hant': '馬加比四'},
{'index': '58', 'en': 'Ode', 'de': 'Ode', 'es': 'Oda', 'pt': 'Od', 'ko': '오데', 'zh-Hans': 'Odes', 'zh-Hant': 'Odes'},
{'index': '59', 'en': 'Ps Sol', 'de': 'Ps Sal', 'es': 'S Sal', 'pt': 'Salmos de Salomão', 'ko': '솔로몬의 시편', 'zh-Hans': 'Psalms of Solomon', 'zh-Hant': 'Psalms of Solomon'},
{'index': '60', 'en': 'Laod', 'de': 'Laod', 'es': 'Laod', 'pt': 'Epístola aos Laodicenses', 'ko': '라오디게아에 서신', 'zh-Hans': 'Epistle to the Laodiceans', 'zh-Hant': 'Epistle to the Laodiceans'},
{'index': '61', 'en': 'Mt', 'de': 'Mt', 'es': 'Mt', 'pt': 'Mt', 'ko': '마', 'zh-Hans': '太', 'zh-Hant': '太'},
{'index': '62', 'en': 'Mk', 'de': 'Mk', 'es': 'Mr', 'pt': 'Mc', 'ko': '막', 'zh-Hans': '可', 'zh-Hant': '可'},
{'index': '63', 'en': 'Lk', 'de': 'Lk', 'es': 'Lc', 'pt': 'Lc', 'ko': '눅', 'zh-Hans': '路', 'zh-Hant': '路'},
{'index': '64', 'en': 'Jn', 'de': 'Joh', 'es': 'Jn', 'pt': 'Jo', 'ko': '요', 'zh-Hans': '约', 'zh-Hant': '約'},
{'index': '65', 'en': 'Ac', 'de': 'Apg', 'es': 'Hch', 'pt': 'At', 'ko': '행', 'zh-Hans': '徒', 'zh-Hant': '徒'},
{'index': '66', 'en': 'Ro', 'de': 'Röm', 'es': 'Ro', 'pt': 'Rm', 'ko': '롬', 'zh-Hans': '罗', 'zh-Hant': '羅'},
{'index': '67', 'en': '1 Co', 'de': '1Kor', 'es': '1 Co', 'pt': '1Co', 'ko': '고전', 'zh-Hans': '林前', 'zh-Hant': '林前'},
{'index': '68', 'en': '2 Co', 'de': '2Kor', 'es': '2 Co', 'pt': '2Co', 'ko': '고후', 'zh-Hans': '林后', 'zh-Hant': '林後'},
{'index': '69', 'en': 'Ga', 'de': 'Gal', 'es': 'Gl', 'pt': 'Gl', 'ko': '갈', 'zh-Hans': '加', 'zh-Hant': '加'},
{'index': '70', 'en': 'Eph', 'de': 'Eph', 'es': 'Ef', 'pt': 'Ef', 'ko': '엡', 'zh-Hans': '弗', 'zh-Hant': '弗'},
{'index': '71', 'en': 'Php', 'de': 'Php', 'es': 'Flp', 'pt': 'Fp', 'ko': '빌', 'zh-Hans': '腓', 'zh-Hant': '腓'},
{'index': '72', 'en': 'Col', 'de': 'Kol', 'es': 'Col', 'pt': 'Cl', 'ko': '골', 'zh-Hans': '西', 'zh-Hant': '西'},
{'index': '73', 'en': '1 Th', 'de': '1Th', 'es': '1 Tes', 'pt': '1Ts', 'ko': '살전', 'zh-Hans': '帖前', 'zh-Hant': '帖前'},
{'index': '74', 'en': '2 Th', 'de': '2Th', 'es': '2 Tes', 'pt': '2Ts', 'ko': '살후', 'zh-Hans': '帖后', 'zh-Hant': '帖後'},
{'index': '75', 'en': '1 Ti', 'de': '1Ti', 'es': '1 Ti', 'pt': '1Tm', 'ko': '딤전', 'zh-Hans': '提前', 'zh-Hant': '提前'},
{'index': '76', 'en': '2 Ti', 'de': '2Ti', 'es': '2 Ti', 'pt': '2Tm', 'ko': '딤후', 'zh-Hans': '提后', 'zh-Hant': '提後'},
{'index': '77', 'en': 'Tt', 'de': 'Tit', 'es': 'Tit', 'pt': 'Tt', 'ko': '딛', 'zh-Hans': '多', 'zh-Hant': '多'},
{'index': '78', 'en': 'Phm', 'de': 'Phlm', 'es': 'Flm', 'pt': 'Fm', 'ko': '몬', 'zh-Hans': '门', 'zh-Hant': '門'},
{'index': '79', 'en': 'Heb', 'de': 'Heb', 'es': 'He', 'pt': 'Hb', 'ko': '히', 'zh-Hans': '来', 'zh-Hant': '來'},
{'index': '80', 'en': 'Jas', 'de': 'Jak', 'es': 'Stg', 'pt': 'Tg', 'ko': '약', 'zh-Hans': '雅', 'zh-Hant': '雅'},
{'index': '81', 'en': '1 Pe', 'de': '1Pe', 'es': '1 P', 'pt': '1Pe', 'ko': '벧전', 'zh-Hans': '彼前', 'zh-Hant': '彼前'},
{'index': '82', 'en': '2 Pe', 'de': '2Pe', 'es': '2 P', 'pt': '2Pe', 'ko': '벧후', 'zh-Hans': '彼后', 'zh-Hant': '彼後'},
{'index': '83', 'en': '1 Jn', 'de': '1Joh', 'es': '1 Jn', 'pt': '1Jo', 'ko': '요일', 'zh-Hans': '约壹', 'zh-Hant': '約壹'},
{'index': '84', 'en': '2 Jn', 'de': '2Joh', 'es': '2 Jn', 'pt': '2Jo', 'ko': '요이', 'zh-Hans': '约貳', 'zh-Hant': '約貳'},
{'index': '85', 'en': '3 Jn', 'de': '3Joh', 'es': '3 Jn', 'pt': '3Jo', 'ko': '요삼', 'zh-Hans': '约叁', 'zh-Hant': '約叁'},
{'index': '86', 'en': 'Jud', 'de': 'Jud', 'es': 'Jud', 'pt': 'Jd', 'ko': '유', 'zh-Hans': '犹', 'zh-Hant': '猶'},
{'index': '87', 'en': 'Re', 'de': 'Offb', 'es': 'Ap', 'pt': 'Ap', 'ko': '계', 'zh-Hans': '启', 'zh-Hant': '啟'},
]
