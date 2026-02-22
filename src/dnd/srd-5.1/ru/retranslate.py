#!/usr/bin/env python3
"""
Complete re-translation of spells section (lines 229+) from EN original.
Keeps the intro (lines 0-228) from the already-translated RU file.
Applies all translations to the original EN text to avoid double-translation issues.
"""
import re, sys

EN_FILE = "/Users/petrradilov/Documents/srd/dndsrd5.2_markdown/src/dnd/srd-5.1/en/10_Spells.md"
RU_FILE = "/Users/petrradilov/Documents/srd/dndsrd5.2_markdown/src/dnd/srd-5.1/ru/10_Spells.md"

with open(EN_FILE, "r", encoding="utf-8") as f:
    en_lines = f.read().split('\n')
with open(RU_FILE, "r", encoding="utf-8") as f:
    ru_lines = f.read().split('\n')

N = len(en_lines)

# Spell name mapping
SN = {
    "Acid Splash":"Кислотные брызги","Chill Touch":"Могильный холод","Dancing Lights":"Танцующие огоньки",
    "Druidcraft":"Искусство друидов","Eldritch Blast":"Мистический заряд","Fire Bolt":"Огненный снаряд",
    "Guidance":"Указание","Light":"Свет","Mage Hand":"Волшебная рука","Mending":"Починка",
    "Message":"Сообщение","Minor Illusion":"Малая иллюзия","Poison Spray":"Ядовитые брызги",
    "Prestidigitation":"Фокусы","Produce Flame":"Сотворение пламени","Ray of Frost":"Луч холода",
    "Resistance":"Сопротивление","Sacred Flame":"Священное пламя","Shillelagh":"Дубинка",
    "Shocking Grasp":"Шоковый захват","Spare the Dying":"Сопровождение умирающего",
    "Thaumaturgy":"Тауматургия","True Strike":"Верный удар","Vicious Mockery":"Язвительная насмешка",
    "Alarm":"Тревога","Animal Friendship":"Дружба с животными","Bane":"Порча","Bless":"Благословение",
    "Burning Hands":"Огненные руки","Charm Person":"Очарование личности","Color Spray":"Цветные брызги",
    "Command":"Приказ","Comprehend Languages":"Понимание языков",
    "Create or Destroy Water":"Сотворение или уничтожение воды","Cure Wounds":"Лечение ран",
    "Detect Evil and Good":"Обнаружение добра и зла","Detect Magic":"Обнаружение магии",
    "Detect Poison and Disease":"Обнаружение яда и болезни","Disguise Self":"Маскировка",
    "Divine Favor":"Божественное благоволение","Entangle":"Опутывание",
    "Expeditious Retreat":"Поспешное отступление","Faerie Fire":"Огонь фей","False Life":"Псевдожизнь",
    "Feather Fall":"Падение пёрышком","Find Familiar":"Поиск фамильяра","Floating Disk":"Парящий диск",
    "Fog Cloud":"Туманное облако","Goodberry":"Чудо-ягоды","Grease":"Скольжение",
    "Guiding Bolt":"Направляющий снаряд","Healing Word":"Целебное слово",
    "Hellish Rebuke":"Адское возмездие","Heroism":"Героизм","Hideous Laughter":"Жуткий смех",
    "Hunter's Mark":"Метка охотника","Identify":"Опознание","Illusory Script":"Иллюзорный текст",
    "Inflict Wounds":"Нанесение ран","Jump":"Прыжок","Longstrider":"Скороход",
    "Mage Armor":"Доспехи мага","Magic Missile":"Магическая стрела",
    "Protection from Evil and Good":"Защита от добра и зла","Purify Food and Drink":"Очистить пищу и питьё",
    "Sanctuary":"Святилище","Shield":"Щит","Shield of Faith":"Щит веры","Silent Image":"Немой образ",
    "Sleep":"Усыпление","Speak with Animals":"Разговор с животными","Thunderwave":"Волна грома",
    "Unseen Servant":"Невидимый слуга","Acid Arrow":"Кислотная стрела","Aid":"Помощь",
    "Alter Self":"Смена обличья","Animal Messenger":"Животный посланник","Arcane Lock":"Арканный замок",
    "Arcanist's Magic Aura":"Аура арканиста","Augury":"Предсказание","Barkskin":"Кора",
    "Blindness/Deafness":"Слепота/Глухота","Blur":"Размытость","Branding Smite":"Клеймящая кара",
    "Calm Emotions":"Успокоение эмоций","Continual Flame":"Вечный огонь","Darkness":"Тьма",
    "Darkvision":"Тёмное зрение","Detect Thoughts":"Обнаружение мыслей",
    "Enhance Ability":"Улучшение характеристики","Enlarge/Reduce":"Увеличение/уменьшение",
    "Enthrall":"Завораживание","Find Steed":"Поиск скакуна","Find Traps":"Поиск ловушек",
    "Flame Blade":"Пылающий клинок","Flaming Sphere":"Пылающая сфера",
    "Gentle Repose":"Бальзамирование","Gust of Wind":"Порыв ветра","Heat Metal":"Раскалённый металл",
    "Hold Person":"Удержание личности","Invisibility":"Невидимость","Knock":"Открывание",
    "Lesser Restoration":"Малое восстановление","Levitate":"Левитация",
    "Locate Animals or Plants":"Поиск животных или растений","Locate Object":"Поиск объекта",
    "Magic Mouth":"Волшебные уста","Magic Weapon":"Волшебное оружие","Mirror Image":"Отражения",
    "Misty Step":"Туманный шаг","Moonbeam":"Лунный луч","Pass without Trace":"Бесследное передвижение",
    "Prayer of Healing":"Молитва исцеления","Protection from Poison":"Защита от яда",
    "Ray of Enfeeblement":"Луч ослабления","Rope Trick":"Верёвочный фокус",
    "Scorching Ray":"Палящий луч","See Invisibility":"Видение невидимого","Shatter":"Дребезги",
    "Silence":"Тишина","Spider Climb":"Паучье лазание","Spike Growth":"Шипы",
    "Spiritual Weapon":"Духовное оружие","Suggestion":"Внушение","Warding Bond":"Защитные узы",
    "Web":"Паутина","Zone of Truth":"Зона правды","Animate Dead":"Оживление мёртвых",
    "Beacon of Hope":"Маяк надежды","Bestow Curse":"Наложение проклятия","Blink":"Мерцание",
    "Call Lightning":"Молния с небес","Clairvoyance":"Ясновидение",
    "Conjure Animals":"Призыв животных","Counterspell":"Контрзаклинание",
    "Create Food and Water":"Сотворение пищи и воды","Daylight":"Дневной свет",
    "Dispel Magic":"Рассеивание магии","Fear":"Страх","Fireball":"Огненный шар","Fly":"Полёт",
    "Gaseous Form":"Газообразная форма","Glyph of Warding":"Охранные руны","Haste":"Ускорение",
    "Hypnotic Pattern":"Гипнотический узор","Lightning Bolt":"Молния",
    "Magic Circle":"Магический круг","Major Image":"Высший образ",
    "Mass Healing Word":"Массовое целебное слово","Meld into Stone":"Слияние с камнем",
    "Nondetection":"Необнаружимость","Phantom Steed":"Призрачный скакун",
    "Plant Growth":"Рост растений","Protection from Energy":"Защита от энергии",
    "Remove Curse":"Снятие проклятия","Revivify":"Возвращение к жизни","Sending":"Послание",
    "Sleet Storm":"Слякотный дождь","Slow":"Замедление","Speak with Dead":"Разговор с мёртвыми",
    "Speak with Plants":"Разговор с растениями","Spirit Guardians":"Духовные стражи",
    "Stinking Cloud":"Удушающее облако","Tiny Hut":"Крошечная хижина","Tongues":"Языки",
    "Vampiric Touch":"Прикосновение вампира","Water Breathing":"Дыхание под водой",
    "Water Walk":"Хождение по воде","Wind Wall":"Стена ветра","Arcane Eye":"Арканный глаз",
    "Banishment":"Изгнание","Black Tentacles":"Чёрные щупальца","Blight":"Гниль",
    "Compulsion":"Принуждение","Confusion":"Замешательство",
    "Conjure Minor Elementals":"Призыв малых элементалей",
    "Conjure Woodland Beings":"Призыв лесных существ","Control Water":"Власть над водой",
    "Death Ward":"Защита от смерти","Dimension Door":"Дверь измерений","Divination":"Гадание",
    "Dominate Beast":"Подчинение зверя","Fabricate":"Фабрикация","Faithful Hound":"Верный пёс",
    "Fire Shield":"Огненный щит","Freedom of Movement":"Свобода перемещения",
    "Giant Insect":"Гигантское насекомое","Greater Invisibility":"Высшая невидимость",
    "Guardian of Faith":"Страж веры","Hallucinatory Terrain":"Иллюзорная местность",
    "Ice Storm":"Град","Locate Creature":"Поиск существа","Phantasmal Killer":"Призрачный убийца",
    "Polymorph":"Превращение","Private Sanctum":"Личное убежище",
    "Resilient Sphere":"Упругая сфера","Secret Chest":"Тайный сундук",
    "Stone Shape":"Изменение формы камня","Stoneskin":"Каменная кожа","Wall of Fire":"Стена огня",
    "Animate Objects":"Оживление предметов","Antilife Shell":"Барьер жизни",
    "Arcane Hand":"Арканная рука","Awaken":"Пробуждение","Cloudkill":"Облако убийства",
    "Commune":"Причастие","Commune with Nature":"Связь с природой","Cone of Cold":"Конус холода",
    "Conjure Elemental":"Сотворение элементаля","Contact Other Plane":"Связь с иным планом",
    "Contagion":"Заражение","Creation":"Сотворение","Dispel Evil and Good":"Рассеивание добра и зла",
    "Dominate Person":"Подчинение личности","Dream":"Сон","Flame Strike":"Небесный огонь",
    "Geas":"Обет","Greater Restoration":"Высшее восстановление","Hallow":"Освящение",
    "Hold Monster":"Удержание чудовища","Insect Plague":"Нашествие насекомых",
    "Legend Lore":"Знание легенд","Mass Cure Wounds":"Массовое исцеление ран",
    "Mislead":"Введение в заблуждение","Modify Memory":"Изменение памяти","Passwall":"Проход",
    "Planar Binding":"Планарные узы","Raise Dead":"Воскрешение мёртвых",
    "Reincarnate":"Реинкарнация","Scrying":"Наблюдение","Seeming":"Ложный облик",
    "Telekinesis":"Телекинез","Telepathic Bond":"Телепатическая связь",
    "Teleportation Circle":"Круг телепортации","Tree Stride":"Шаг сквозь деревья",
    "Wall of Force":"Стена силы","Wall of Stone":"Каменная стена",
    "Blade Barrier":"Стена клинков","Chain Lightning":"Цепная молния",
    "Circle of Death":"Круг смерти","Conjure Fey":"Сотворение феи",
    "Contingency":"Предусмотрительность","Create Undead":"Создание нежити",
    "Disintegrate":"Распыление","Eyebite":"Зловещий взгляд","Find the Path":"Поиск пути",
    "Flesh to Stone":"Окаменение","Forbiddance":"Запрет","Freezing Sphere":"Морозная сфера",
    "Globe of Invulnerability":"Сфера неуязвимости","Guards and Wards":"Стражи и обереги",
    "Harm":"Нанесение вреда","Heal":"Исцеление","Heroes' Feast":"Пир героев",
    "Instant Summons":"Мгновенный призыв","Irresistible Dance":"Непреодолимый танец",
    "Magic Jar":"Волшебный сосуд","Mass Suggestion":"Массовое внушение",
    "Move Earth":"Движение земли","Planar Ally":"Планарный союзник",
    "Programmed Illusion":"Запрограммированная иллюзия","Sunbeam":"Солнечный луч",
    "Transport via Plants":"Перемещение растениями","True Seeing":"Видение истины",
    "Wall of Ice":"Стена льда","Wall of Thorns":"Стена тернов","Wind Walk":"Хождение по ветру",
    "Word of Recall":"Слово возврата","Arcane Sword":"Арканный меч",
    "Conjure Celestial":"Призыв небожителя","Delayed Blast Fireball":"Замедленный огненный шар",
    "Divine Word":"Божественное слово","Etherealness":"Эфирность","Finger of Death":"Перст смерти",
    "Fire Storm":"Огненная буря","Forcecage":"Силовая клетка",
    "Magnificent Mansion":"Великолепный особняк","Mirage Arcane":"Мираж",
    "Plane Shift":"Переход между планами","Prismatic Spray":"Радужные брызги",
    "Project Image":"Проецирование образа","Regenerate":"Регенерация",
    "Resurrection":"Воскрешение","Reverse Gravity":"Разворот гравитации","Sequester":"Изоляция",
    "Simulacrum":"Симулякр","Symbol":"Символ","Teleport":"Телепорт",
    "Animal Shapes":"Животные формы","Antimagic Field":"Антимагическое поле",
    "Antipathy/Sympathy":"Антипатия/Симпатия","Clone":"Клон",
    "Control Weather":"Власть над погодой","Demiplane":"Полуплан",
    "Dominate Monster":"Подчинение чудовища","Earthquake":"Землетрясение",
    "Feeblemind":"Помрачение","Glibness":"Дар красноречия","Holy Aura":"Аура святости",
    "Incendiary Cloud":"Огненное облако","Maze":"Лабиринт","Mind Blank":"Пустой разум",
    "Power Word Stun":"Слово силы: оглушение","Sunburst":"Солнечный удар",
    "Astral Projection":"Астральная проекция","Foresight":"Предвидение","Gate":"Врата",
    "Imprisonment":"Заточение","Mass Heal":"Массовое исцеление","Meteor Swarm":"Метеоритный дождь",
    "Power Word Kill":"Слово силы: смерть","Prismatic Wall":"Радужная стена",
    "Shapechange":"Изменение формы","Storm of Vengeance":"Буря возмездия",
    "Time Stop":"Остановка времени","True Polymorph":"Истинный полиморф",
    "True Resurrection":"Истинное воскрешение","Weird":"Кошмар","Wish":"Исполнение желаний",
}

CN = {"Bard":"Бард","Cleric":"Жрец","Druid":"Друид","Paladin":"Паладин","Ranger":"Следопыт",
      "Sorcerer":"Чародей","Warlock":"Колдун","Wizard":"Волшебник"}

SCH = {"Abjuration":"Ограждение","Conjuration":"Вызов","Divination":"Прорицание",
       "Enchantment":"Очарование","Evocation":"Воплощение","Illusion":"Иллюзия",
       "Necromancy":"Некромантия","Transmutation":"Преобразование"}

SCH_GEN = {"Ограждение":"Ограждения","Вызов":"Вызова","Прорицание":"Прорицания",
           "Очарование":"Очарования","Воплощение":"Воплощения","Иллюзия":"Иллюзии",
           "Некромантия":"Некромантии","Преобразование":"Преобразования"}

MATS = {
    "(a tiny bell and a piece of fine silver wire)":"(крошечный колокольчик и кусочек тонкой серебряной проволоки)",
    "(a bit of phosphorus or wychwood, or a glowworm)":"(кусочек фосфора или гнилушки, или светлячок)",
    "(a firefly or phosphorescent moss)":"(светлячок или фосфоресцирующий мох)",
    "(two lodestones)":"(два магнитных камня)",
    "(a short piece of copper wire)":"(короткий кусок медной проволоки)",
    "(a bit of fleece)":"(кусочек овечьей шерсти)",
    "(mistletoe, a shamrock leaf, and a club or quarterstaff)":"(омела, лист клевера и дубинка или боевой посох)",
    "(a miniature cloak)":"(миниатюрный плащ)",
    "(a drop of blood)":"(капля крови)",
    "(a sprinkling of holy water)":"(капля святой воды)",
    "(a tiny strip of white cloth)":"(крошечная полоска белой ткани)",
    "(a pinch of fine sand, rose petals, or crickets)":"(щепотка мелкого песка, лепестки роз или сверчки)",
    "(a tiny ball of bat guano and sulfur)":"(крошечный шарик из помёта летучей мыши и серы)",
    "(a piece of string and a bit of wood)":"(кусок верёвки и щепка дерева)",
    "(a pinch of sand)":"(щепотка песка)",
    "(a snake's tongue and either a bit of honeycomb or a drop of sweet oil)":"(змеиный язык и либо кусочек медовых сот, либо капля сладкого масла)",
    "(a small square piece of silk)":"(маленький квадратный кусок шёлка)",
    "(a bit of spider web)":"(кусочек паутины)",
    "(diamonds worth 300 gp, which the spell consumes)":"(бриллианты стоимостью 300 зм, расходуемые заклинанием)",
    "(a bit of phosphorus)":"(кусочек фосфора)",
}

# Level section headings
LEVEL_HEADINGS = {
    "## Cantrips (Level 0)":"## Заговоры (уровень 0)",
    "## Level 1 Spells":"## Заклинания 1-го уровня",
    "## Level 2 Spells":"## Заклинания 2-го уровня",
    "## Level 3 Spells":"## Заклинания 3-го уровня",
    "## Level 4 Spells":"## Заклинания 4-го уровня",
    "## Level 5 Spells":"## Заклинания 5-го уровня",
    "## Level 6 Spells":"## Заклинания 6-го уровня",
    "## Level 7 Spells":"## Заклинания 7-го уровня",
    "## Level 8 Spells":"## Заклинания 8-го уровня",
    "## Level 9 Spells":"## Заклинания 9-го уровня",
}

def tr_school_line(line):
    m = re.match(r'^\*(Level (\d+) )?(\w+)( Cantrip)? \(([^)]+)\)\*\s*$', line)
    if not m: return line
    lvl = m.group(2); sch = m.group(3); cantrip = m.group(4); cls = m.group(5)
    sch_ru = SCH.get(sch, sch)
    cls_parts = [c.strip() for c in cls.split(",")]
    cls_ru = ", ".join(CN.get(c, c) for c in cls_parts)
    if cantrip:
        return f"*Заговор {SCH_GEN.get(sch_ru, sch_ru)} ({cls_ru})*"
    return f"*{sch_ru} {lvl}-го уровня ({cls_ru})*"

def tr_ct(rest):
    rest = rest.replace("Bonus Action", "Бонусное действие")
    rest = rest.replace("Action", "Действие")
    rest = rest.replace("Reaction", "Реакция")
    rest = rest.replace("or Ritual", "или Ритуал")
    rest = re.sub(r'(\d+) minutes?\b', lambda m: f"{m.group(1)} минута" if int(m.group(1))==1 else f"{m.group(1)} минут", rest)
    rest = re.sub(r'(\d+) hours?\b', lambda m: f"{m.group(1)} час" if int(m.group(1))==1 else f"{m.group(1)} часов" if int(m.group(1))>=5 else f"{m.group(1)} часа", rest)
    return rest

def tr_range(rest):
    rest = re.sub(r'Self \((\d+)-foot cone\)', lambda m: f'На себя ({m.group(1)}-футовый конус)', rest)
    rest = re.sub(r'Self \((\d+)-foot-radius sphere\)', lambda m: f'На себя (сфера радиусом {m.group(1)} футов)', rest)
    rest = re.sub(r'Self \((\d+)-foot radius\)', lambda m: f'На себя (радиус {m.group(1)} футов)', rest)
    rest = re.sub(r'Self \((\d+)-foot line\)', lambda m: f'На себя ({m.group(1)}-футовая линия)', rest)
    rest = re.sub(r'Self \((\d+)-foot-radius hemisphere\)', lambda m: f'На себя (полусфера радиусом {m.group(1)} футов)', rest)
    rest = re.sub(r'Self \((\d+)-foot cube\)', lambda m: f'На себя ({m.group(1)}-футовый куб)', rest)
    rest = rest.replace("Self", "На себя").replace("Touch", "Касание").replace("Unlimited", "Неограниченная").replace("Special", "Особая")
    rest = re.sub(r'(\d+) feet\b', lambda m: f"{m.group(1)} футов", rest)
    rest = re.sub(r'(\d+)-foot\b', lambda m: f"{m.group(1)}-футов", rest)
    rest = re.sub(r'(\d+) miles?\b', lambda m: f"{m.group(1)} миль" if int(m.group(1))>=5 else f"{m.group(1)} мили" if int(m.group(1))>=2 else f"{m.group(1)} миля", rest)
    return rest

def tr_comp(rest):
    rest = re.sub(r'\bV\b', 'В', rest)
    rest = re.sub(r'\bS\b', 'С', rest)
    rest = re.sub(r'\bM\b', 'М', rest)
    for en, ru in MATS.items():
        if en in rest:
            rest = rest.replace(en, ru)
            break
    # Generic material component translation for unmatched ones
    # Translate gp in components
    rest = re.sub(r'(\d[\d,]*) gp\b', lambda m: f"{m.group(1)} зм", rest)
    return rest

def tr_dur(text):
    text = text.replace("Instantaneous", "Мгновенная")
    text = text.replace("Concentration, up to ", "Концентрация, вплоть до ")
    text = text.replace("Up to ", "Вплоть до ")
    text = text.replace("Until dispelled or triggered", "Пока не будет рассеяно или активировано")
    text = text.replace("Until dispelled", "Пока не будет рассеяно")
    text = text.replace("Special", "Особая")
    text = text.replace("one minute", "1 минуту")
    text = text.replace("one hour", "1 час")
    def ru_min(m):
        n=int(m.group(1))
        if n==1: return f"{n} минуту"
        elif 2<=n<=4: return f"{n} минуты"
        else: return f"{n} минут"
    def ru_hr(m):
        n=int(m.group(1))
        if n==1: return f"{n} час"
        elif 2<=n<=4: return f"{n} часа"
        else: return f"{n} часов"
    def ru_rnd(m):
        n=int(m.group(1))
        if n==1: return f"{n} раунд"
        elif 2<=n<=4: return f"{n} раунда"
        else: return f"{n} раундов"
    def ru_day(m):
        n=int(m.group(1))
        if n==1: return f"{n} день"
        elif 2<=n<=4: return f"{n} дня"
        else: return f"{n} дней"
    text = re.sub(r'(\d+) minutes?\b', ru_min, text)
    text = re.sub(r'(\d+) hours?\b', ru_hr, text)
    text = re.sub(r'(\d+) rounds?\b', ru_rnd, text)
    text = re.sub(r'(\d+) days?\b', ru_day, text)
    return text

def tr_body(line):
    """Comprehensive body text translation from EN."""
    # Structural markers
    line = line.replace("**_At Higher Levels._**", "**_На более высоких уровнях._**")
    line = line.replace("**_Using a Higher-Level Spell Slot._**", "**_Использование ячейки более высокого уровня._**")
    line = line.replace("**_Cantrip Upgrade._**", "**_Усиление заговора._**")

    # Dice: d4->к4
    line = re.sub(r'(\d*)d(\d+)', lambda m: f"{m.group(1)}к{m.group(2)}", line)

    # Currency
    line = re.sub(r'(\d[\d,]*) gp\b', lambda m: f"{m.group(1)} зм", line)
    line = re.sub(r'(\d[\d,]*) sp\b', lambda m: f"{m.group(1)} см", line)
    line = re.sub(r'(\d[\d,]*) cp\b', lambda m: f"{m.group(1)} мм", line)

    # Level references FIRST (before other word replacements)
    line = re.sub(r'\b(\d+)(?:st|nd|rd|th) level\b', lambda m: f"{m.group(1)}-го уровня", line)
    line = re.sub(r'\b(\d+)(?:st|nd|rd|th)-level\b', lambda m: f"{m.group(1)}-го уровня", line)

    # Feet
    line = re.sub(r'(\d+) feet\b', lambda m: f"{m.group(1)} футов", line)
    line = re.sub(r'(\d+)-foot\b', lambda m: f"{m.group(1)}-футов", line)
    line = re.sub(r'(\d+) foot\b', lambda m: f"{m.group(1)} фут", line)
    line = re.sub(r'(\d+) miles?\b', lambda m: f"{m.group(1)} миль" if int(m.group(1))>=5 else f"{m.group(1)} мили" if int(m.group(1))>=2 else f"{m.group(1)} миля", line)

    # Spell names in italics (longest first)
    for en_n, ru_n in sorted(SN.items(), key=lambda x: -len(x[0])):
        line = re.sub(r'\*' + re.escape(en_n) + r'\*', f'*{ru_n}*', line)
        line = re.sub(r'\*' + re.escape(en_n.lower()) + r'\*', f'*{ru_n.lower()}*', line, flags=re.IGNORECASE)

    # Complete sentence/phrase patterns (applied to original EN, longest first)
    phrases = [
        ("When you cast this spell using a spell slot of", "Если вы сотворяете это заклинание, используя ячейку заклинания"),
        ("you can target one additional creature for each slot level above", "вы можете нацелиться на одно дополнительное существо за каждый уровень ячейки выше"),
        ("the damage increases by", "урон увеличивается на"),
        ("for each slot level above", "за каждый уровень ячейки выше"),
        ("This spell's damage increases by", "Урон этого заклинания увеличивается на"),
        ("when you reach", "когда вы достигаете"),
        ("Make a ranged spell attack against the target.", "Совершите дальнобойную атаку заклинанием по цели."),
        ("Make a ranged spell attack against the creature", "Совершите дальнобойную атаку заклинанием по существу"),
        ("Make a ranged spell attack against", "Совершите дальнобойную атаку заклинанием по"),
        ("Make a melee spell attack against the target.", "Совершите рукопашную атаку заклинанием по цели."),
        ("Make a melee spell attack against", "Совершите рукопашную атаку заклинанием по"),
        ("Make a ranged spell attack.", "Совершите дальнобойную атаку заклинанием."),
        ("Make a melee spell attack.", "Совершите рукопашную атаку заклинанием."),
        ("On a hit, the target takes", "При попадании цель получает"),
        ("On a hit, it takes", "При попадании она получает"),
        ("On a hit, the target", "При попадании цель"),
        ("On a hit,", "При попадании"),
        ("On a miss,", "При промахе"),
        ("on a failed save, or half as much damage on a successful one", "при провале спасброска, или половину этого урона при успехе"),
        ("on a failed save", "при провале спасброска"),
        ("on a successful save", "при успешном спасброске"),
        ("on a successful one", "при успехе"),
        ("half as much damage", "половину этого урона"),
        ("A creature takes", "Существо получает"),
        ("The target takes", "Цель получает"),
        ("the target takes", "цель получает"),
        ("must succeed on a Dexterity saving throw or take", "должна преуспеть в спасброске Ловкости или получить"),
        ("must succeed on a Constitution saving throw or take", "должна преуспеть в спасброске Телосложения или получить"),
        ("must succeed on a Wisdom saving throw or take", "должна преуспеть в спасброске Мудрости или получить"),
        ("must succeed on a Charisma saving throw or", "должна преуспеть в спасброске Харизмы, иначе"),
        ("must succeed on a Strength saving throw or", "должна преуспеть в спасброске Силы, иначе"),
        ("must succeed on a Dexterity saving throw or", "должна преуспеть в спасброске Ловкости, иначе"),
        ("must succeed on a Constitution saving throw or", "должна преуспеть в спасброске Телосложения, иначе"),
        ("must succeed on a Wisdom saving throw or", "должна преуспеть в спасброске Мудрости, иначе"),
        ("must succeed on a Intelligence saving throw or", "должна преуспеть в спасброске Интеллекта, иначе"),
        ("must make a Dexterity saving throw", "должна совершить спасбросок Ловкости"),
        ("must make a Constitution saving throw", "должна совершить спасбросок Телосложения"),
        ("must make a Wisdom saving throw", "должна совершить спасбросок Мудрости"),
        ("must make a Charisma saving throw", "должна совершить спасбросок Харизмы"),
        ("must make a Strength saving throw", "должна совершить спасбросок Силы"),
        ("Dexterity saving throw", "спасбросок Ловкости"),
        ("Constitution saving throw", "спасбросок Телосложения"),
        ("Wisdom saving throw", "спасбросок Мудрости"),
        ("Charisma saving throw", "спасбросок Харизмы"),
        ("Strength saving throw", "спасбросок Силы"),
        ("Intelligence saving throw", "спасбросок Интеллекта"),
        ("saving throws", "спасброски"),
        ("saving throw", "спасбросок"),
        ("for the duration", "на время действия заклинания"),
        ("until the spell ends", "пока заклинание не закончится"),
        ("until the start of your next turn", "до начала вашего следующего хода"),
        ("until the end of your next turn", "до конца вашего следующего хода"),
        ("at the start of each of its turns", "в начале каждого своего хода"),
        ("at the end of each of its turns", "в конце каждого своего хода"),
        ("within range", "в пределах дистанции"),
        ("that you can see within", "которое вы видите в пределах"),
        ("you can see within", "видите в пределах"),
        ("you can see", "видите"),
        ("ranged spell attack", "дальнобойную атаку заклинанием"),
        ("melee spell attack", "рукопашную атаку заклинанием"),
        ("spell attack", "атаку заклинанием"),
        ("attack rolls", "броски атаки"),
        ("attack roll", "бросок атаки"),
        ("ability check", "проверку характеристики"),
        ("ability checks", "проверки характеристик"),
        ("spell save DC", "СЛ спасброска от ваших заклинаний"),
        ("your spellcasting ability", "вашу базовую характеристику заклинателя"),
        ("spellcasting ability", "базовая характеристика заклинателя"),
        ("proficiency bonus", "бонус мастерства"),
        ("can't regain hit points", "не может восстанавливать хиты"),
        ("regain hit points", "восстанавливает хиты"),
        ("regains hit points", "восстанавливает хиты"),
        ("temporary hit points", "временные хиты"),
        ("hit points", "хитов"),
        ("hit point", "хит"),
        ("advantage on", "преимущество при"),
        ("disadvantage on", "помеху при"),
        ("DC", "СЛ"),
        ("AC", "КД"),
        # Damage types
        ("acid damage", "урон кислотой"),
        ("bludgeoning damage", "дробящий урон"),
        ("cold damage", "урон холодом"),
        ("fire damage", "урон огнём"),
        ("force damage", "урон силовым полем"),
        ("lightning damage", "урон электричеством"),
        ("necrotic damage", "некротический урон"),
        ("piercing damage", "колющий урон"),
        ("poison damage", "урон ядом"),
        ("psychic damage", "психический урон"),
        ("radiant damage", "урон излучением"),
        ("slashing damage", "рубящий урон"),
        ("thunder damage", "урон громом"),
        ("Player's Handbook", "*Книга игрока*"),
        ("the GM", "Мастер"),
        ("The GM", "Мастер"),
    ]

    for en, ru in phrases:
        line = line.replace(en, ru)

    return line

# Build output
out = list(ru_lines[:229])  # Keep intro (already translated)

for i in range(229, N):
    en = en_lines[i]

    if not en.strip():
        out.append(en); continue

    # Level section headings
    if en in LEVEL_HEADINGS:
        out.append(LEVEL_HEADINGS[en]); continue

    # Spell heading ### SpellName
    m = re.match(r'^(###) ([A-Z].+)$', en)
    if m:
        sn = m.group(2).strip()
        sr = SN.get(sn)
        if sr:
            out.append(f"### {sr} ({sn})")
        else:
            out.append(en)
        continue

    # School/level line
    if re.match(r'^\*(Level \d+ )?\w+( Cantrip)? \(', en):
        out.append(tr_school_line(en)); continue

    # Casting Time
    if en.startswith("**Casting Time:**"):
        rest = en[len("**Casting Time:**"):].strip()
        out.append(f"**Время накладывания:** {tr_ct(rest)}"); continue

    # Range
    if en.startswith("**Range:**"):
        rest = en[len("**Range:**"):].strip()
        out.append(f"**Дистанция:** {tr_range(rest)}"); continue

    # Components
    if en.startswith("**Components:**"):
        rest = en[len("**Components:**"):].strip()
        out.append(f"**Компоненты:** {tr_comp(rest)}"); continue

    # Duration
    if en.startswith("**Duration:**"):
        rest = en[len("**Duration:**"):].strip()
        out.append(f"**Длительность:** {tr_dur(rest)}"); continue

    # Body text
    out.append(tr_body(en))

# Verify
if len(out) != N:
    print(f"ERROR: {N} vs {len(out)}", file=sys.stderr)
    while len(out) < N: out.append("")
    out = out[:N]

with open(RU_FILE, "w", encoding="utf-8") as f:
    f.write('\n'.join(out))

print(f"OK: {len(out)} lines")
