# 신앙 서적 리뷰 #1 — 존 번연 『천로역정』 (새 양식)
# (번호, 배경, 진행단계, 한국어, 영어, 종류)  종류: q / quote / final / label / title / book
EP = 1
BOOK = {"ko": "천로역정", "en": "The Pilgrim's Progress", "author_ko": "존 번연", "author_en": "John Bunyan", "year": "1678"}
PARTS = ["열며", "책과 저자", "순례의 길", "남긴 것", "묻다"]
MUSIC = {"hymn": "amazing_grace", "seed": 1}
ORIG = {"file": "orig.jpg", "fallback": "oldbook", "credit": "1678년 초판 속표지 · Wikimedia Commons (Public Domain)"}
CREDITS = {"oldbook": "Parth Mishra", "road": "Harsh Gupta", "light": "Diego PH", "map": "Ruth Bourke", "pots": "Annie Spratt",
           "prison": "clement proust", "burden": "British Library", "mud": "Jake Warren", "gate": "Danielle Suijkerbuijk",
           "cross": "kiryl", "hill": "Mateusz Sobczak", "valley": "Peter Secan", "market": "Tom Juggins", "castle": "Jonny Gios",
           "key": "Joshua Hoehne", "river": "Andrew Svk", "backpack": "Alex Moliski"}
LONG = {41: 7.0}
CARDS = [
 (1, "oldbook", 0, "우리는 모두\n어딘가로 가는 길 위에 있다.", "We are all on a road, going somewhere.", "q"),
 (2, "oldbook", 0, "그렇다면 그 길의 끝에는\n무엇이 있을까?", "Then what lies at the end of that road?", "q"),
 (3, "ORIG", 0, "1678년 런던에서 나온 첫판 속표지", "The Pilgrim's Progress  ·  first edition, London, 1678", "book"),
 (4, "road", 0, "천로역정", "The Pilgrim's Progress  ·  John Bunyan, 1678", "title"),
 (5, "light", 1, "성경 다음으로 가장 많이 읽힌\n책 가운데 하나로 꼽히는 신앙의 고전.", "Often counted among the most widely read books after the Bible.", "q"),
 (6, "map", 1, "이 책은 꿈 이야기다.\n“나는 잠이 들었고, 꿈을 꾸었다.”", "It is told as a dream: “As I slept, I dreamed a dream.”", "q"),
 (7, "map", 1, "인물과 장소 하나하나가\n신앙의 경험을 뜻하는\n알레고리, 곧 비유 이야기다.", "An allegory — every person and place stands for an experience of faith.", "q"),
 (8, "pots", 1, "지은이 존 번연은\n솥과 냄비를 고치던 땜장이였다.", "Its author, John Bunyan, was a tinker who mended pots and pans.", "q"),
 (9, "pots", 1, "학교 공부는 짧았지만\n성경을 읽고 또 읽으며 설교자가 되었다.", "His schooling was short, but reading the Bible again and again, he became a preacher.", "q"),
 (10, "prison", 1, "1660년, 허가 없이 설교했다는 이유로\n그는 베드퍼드 감옥에 갇혔다.", "In 1660 he was jailed in Bedford for preaching without a license.", "q"),
 (11, "prison", 1, "갇혀 지낸 세월은 12년.\n이 이야기는 감옥에서 구상된 것으로 알려져 있다.", "He spent twelve years in prison, where this story is said to have taken shape.", "q"),
 (12, "light", 1, "1678년,\n마침내 책이 세상에 나왔다.", "In 1678, the book was finally published.", "q"),
 (13, "burden", 2, "순례의 길 ①\n짐을 진 사람", "The Journey 1  ·  The Man with a Burden", "label"),
 (14, "burden", 2, "‘멸망의 도시’에 사는 크리스천.\n그의 등에는 무거운 짐이 있다.", "Christian lives in the City of Destruction, with a heavy burden on his back.", "q"),
 (15, "burden", 2, "그 짐은 죄.\n아무리 애써도 내려놓을 수 없는 무게다.", "The burden is sin — a weight he cannot put down, however hard he tries.", "q"),
 (16, "road", 2, "전도자가 가리킨 빛을 따라\n그는 집을 나서 길을 떠난다.", "Following the light Evangelist points to, he leaves home and sets out.", "q"),
 (17, "mud", 2, "얼마 못 가 그는\n‘낙심의 늪’에 빠진다.", "Before long he sinks into the Slough of Despond.", "q"),
 (18, "mud", 2, "‘도움’이라는 사람이 손을 내밀어\n그를 끌어낸다.", "A man named Help reaches out and pulls him free.", "q"),
 (19, "gate", 2, "마침내 ‘좁은 문’ 앞.\n두드리는 자에게 문이 열린다.", "At last, the Wicket Gate — opened to the one who knocks.", "q"),
 (20, "cross", 2, "순례의 길 ②\n십자가 앞에서", "The Journey 2  ·  At the Cross", "label"),
 (21, "cross", 2, "언덕 위 십자가를 바라보는 순간,\n등의 짐이 풀려 굴러떨어진다.", "The moment he looks at the cross on the hill, the burden comes loose and rolls away.", "q"),
 (22, "cross", 2, "“그분은 슬픔으로 내게 안식을,\n죽음으로 내게 생명을 주셨다.”", "“He hath given me rest by his sorrow, and life by his death.”", "quote"),
 (23, "hill", 2, "그러나 길은 끝나지 않았다.\n가파른 ‘곤고의 언덕’을 오르고,", "But the road goes on. He climbs the steep Hill Difficulty,", "q"),
 (24, "valley", 2, "‘사망의 그늘 골짜기’를\n홀로 지난다.", "and passes alone through the Valley of the Shadow of Death.", "q"),
 (25, "market", 2, "순례의 길 ③\n허영의 시장", "The Journey 3  ·  Vanity Fair", "label"),
 (26, "market", 2, "명예도, 쾌락도, 사람의 영혼까지도\n사고파는 ‘허영의 시장’.", "Vanity Fair, where honor, pleasure — even souls — are bought and sold.", "q"),
 (27, "market", 2, "함께 걷던 신실은 그곳에서\n믿음을 지키다 순교한다.", "There his companion Faithful keeps the faith and is martyred.", "q"),
 (28, "castle", 2, "새 길벗 소망과 함께 샛길로 들어섰다가\n거인 ‘절망’의 ‘의심의 성’에 갇힌다.", "Taking a side path with his new friend Hopeful, he is caught by Giant Despair in Doubting Castle.", "q"),
 (29, "key", 2, "그때 크리스천은 기억해 낸다.\n품속에 ‘약속’이라는 열쇠가 있었다는 것을.", "Then Christian remembers: in his bosom is a key called Promise.", "q"),
 (30, "river", 2, "마지막 관문은\n다리 없는 깊은 강.", "The last trial is a deep river with no bridge.", "q"),
 (31, "river", 2, "가라앉는 크리스천에게 소망이 외친다.\n“형제여, 바닥이 느껴집니다. 단단합니다!”", "Hopeful calls to the sinking Christian: “Be of good cheer, my brother, I feel the bottom, and it is good.”", "q"),
 (32, "light", 2, "강을 건넌 두 순례자는\n마침내 천성의 문에 이른다.", "Across the river, the two pilgrims reach the gate of the Celestial City.", "q"),
 (33, "road", 3, "이 책이 남긴 것", "What the Book Leaves Us", "label"),
 (34, "road", 3, "신앙은 한 번의 결심이 아니라\n끝까지 걸어가는 순례다.", "Faith is not a single decision but a pilgrimage walked to the end.", "q"),
 (35, "cross", 3, "짐은 내 힘으로 벗는 것이 아니라\n십자가 앞에서 벗겨진다.", "The burden is not thrown off by our own strength; it falls away at the cross.", "q"),
 (36, "backpack", 3, "그리고 그 길은 혼자가 아니다.\n신실과 소망 같은 길벗이 있다.", "And no one walks it alone: there are companions like Faithful and Hopeful.", "q"),
 (37, "valley", 3, "물론 아쉬움도 있다.\n크리스천은 아내와 아이들을 두고 홀로 떠난다.", "There are criticisms too: Christian sets out alone, leaving his wife and children behind.", "q"),
 (38, "valley", 3, "구원을 지나치게 개인의 여정으로\n그렸다는 지적이다.", "Some say it paints salvation as too private a journey.", "q"),
 (39, "light", 3, "번연은 1684년 2부를 펴내\n아내 크리스티아나와 아이들의 순례를 그렸다.", "In 1684 Bunyan published Part Two — the pilgrimage of Christian's wife Christiana and their children.", "q"),
 (40, "backpack", 4, "지금 당신의 등에 있는\n무거운 짐은 무엇인가?", "What heavy burden is on your back right now?", "final"),
 (41, "backpack", 4, "그리고 당신은\n어디를 향해 걷고 있는가?", "And where are you walking?", "final"),
 (42, "light", None, "다음 편  ·  아우구스티누스\n『고백록』", "Next  ·  Augustine, Confessions", "label"),
]
