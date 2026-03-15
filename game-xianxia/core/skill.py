"""
修仙游戏 - 功法系统
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Any
from enum import Enum
import math


class SkillType(Enum):
    """功法类型"""
    CULTIVATION = "修炼"      # 修炼心法
    ATTACK = "攻击"           # 攻击术法
    DEFENSE = "防御"          # 防御神通
    SUPPORT = "辅助"          # 辅助功法
    PASSIVE = "被动"          # 被动功法
    SPECIAL = "特殊"          # 特殊功法


class SkillElement(Enum):
    """功法元素属性"""
    NONE = "无"
    METAL = "金"
    WOOD = "木"
    WATER = "水"
    FIRE = "火"
    EARTH = "土"
    THUNDER = "雷"
    ICE = "冰"
    WIND = "风"
    LIGHT = "光"
    DARKNESS = "暗"


class SkillGrade(Enum):
    """功法品阶"""
    MORTAL = ("凡品", 1)
    SPIRIT = ("灵品", 2)
    DIVINE = ("神品", 3)
    CELESTIAL = ("天品", 4)
    
    def __init__(self, grade_name: str, stars: int):
        self.grade_name = grade_name
        self.stars = stars
    
    @property
    def name(self) -> str:
        return self.grade_name


@dataclass
class SkillEffect:
    """功法效果"""
    effect_type: str  # attack, defense, cultivation, heal, buff, debuff, shield, lifesteal, regen, dot, true_damage, hits, counter, invincibility
    base_value: float = 0.0
    per_level: float = 0.0
    element_bonus: float = 1.0  # 元素契合加成
    description: str = ""
    
    def calculate(self, skill_level: int, element_match: float = 1.0) -> float:
        """计算效果值"""
        base = self.base_value + (skill_level - 1) * self.per_level
        return base * self.element_bonus * element_match


@dataclass
class Skill:
    """功法"""
    id: str
    name: str
    type: SkillType
    element: SkillElement = SkillElement.NONE
    grade: SkillGrade = SkillGrade.MORTAL
    
    description: str = ""
    requirement_realm: str = ""  # 境界要求
    requirement_level: int = 1   # 层级要求
    
    # 消耗
    qi_cost: float = 0.0
    cooldown: int = 0  # 冷却回合
    
    # 效果
    effects: List[SkillEffect] = field(default_factory=list)
    passive_effects: Dict[str, float] = field(default_factory=dict)
    
    # 特殊效果 (新增)
    special_effects: Dict[str, Any] = field(default_factory=dict)
    
    # 升级
    max_level: int = 10
    exp_required: List[int] = field(default_factory=lambda: [0] + [100 * (i+1) * i // 2 for i in range(1, 10)])
    
    def get_effect_value(self, effect_type: str, level: int = 1, element_match: float = 1.0) -> float:
        """获取指定类型的效果值"""
        for effect in self.effects:
            if effect.effect_type == effect_type:
                return effect.calculate(level, element_match)
        return 0.0


@dataclass
class PlayerSkill:
    """玩家已学功法"""
    skill_id: str
    level: int = 1
    exp: float = 0.0
    
    @property
    def exp_needed(self) -> int:
        """升级所需经验"""
        skill = SKILLS_DATABASE.get(self.skill_id)
        if not skill:
            return 999999
        if self.level >= skill.max_level:
            return -1  # 满级
        return skill.exp_required[self.level]
    
    @property
    def is_max_level(self) -> bool:
        """是否满级"""
        skill = SKILLS_DATABASE.get(self.skill_id)
        return skill and self.level >= skill.max_level
    
    def add_exp(self, amount: float) -> bool:
        """增加经验，返回是否升级"""
        if self.is_max_level:
            return False
        
        self.exp += amount
        leveled_up = False
        while self.exp >= self.exp_needed and not self.is_max_level:
            self.exp -= self.exp_needed
            self.level += 1
            leveled_up = True
        return leveled_up


# ============ 功法数据库 ============

def _create_cultivation_skill(
    skill_id: str, name: str, element: SkillElement, grade: SkillGrade,
    cultivation_bonus: float, description: str, realm_req: str, level_req: int
) -> Skill:
    """创建修炼功法"""
    return Skill(
        id=skill_id,
        name=name,
        type=SkillType.CULTIVATION,
        element=element,
        grade=grade,
        description=description,
        requirement_realm=realm_req,
        requirement_level=level_req,
        effects=[SkillEffect(
            effect_type="cultivation",
            base_value=cultivation_bonus,
            per_level=cultivation_bonus * 0.1,
            description=f"修炼速度+{cultivation_bonus*100}%"
        )]
    )


def _create_attack_skill(
    skill_id: str, name: str, element: SkillElement, grade: SkillGrade,
    attack: float, qi_cost: float, cooldown: int, description: str, 
    realm_req: str, level_req: int,
    hits: int = 1, true_damage: float = 0.0, lifesteal: float = 0.0,
    buff: str = "", buff_value: float = 0.0, buff_duration: int = 0
) -> Skill:
    """创建攻击功法"""
    effects = [SkillEffect(
        effect_type="attack",
        base_value=attack,
        per_level=attack * 0.15,
        description=f"造成 {attack} 点伤害"
    )]
    
    # 添加特殊效果
    if hits > 1:
        effects.append(SkillEffect(
            effect_type="hits",
            base_value=hits,
            per_level=0,
            description=f"连击 {hits} 次"
        ))
    if true_damage > 0:
        effects.append(SkillEffect(
            effect_type="true_damage",
            base_value=true_damage,
            per_level=true_damage * 0.1,
            description=f"真实伤害 {true_damage}"
        ))
    if lifesteal > 0:
        effects.append(SkillEffect(
            effect_type="lifesteal",
            base_value=lifesteal,
            per_level=lifesteal * 0.05,
            description=f"吸血 {lifesteal*100}%"
        ))
    
    return Skill(
        id=skill_id,
        name=name,
        type=SkillType.ATTACK,
        element=element,
        grade=grade,
        description=description,
        requirement_realm=realm_req,
        requirement_level=level_req,
        qi_cost=qi_cost,
        cooldown=cooldown,
        effects=effects,
        special_effects={"buff": buff, "buff_value": buff_value, "buff_duration": buff_duration}
    )


def _create_defense_skill(
    skill_id: str, name: str, element: SkillElement, grade: SkillGrade,
    defense: float, qi_cost: float, cooldown: int, description: str,
    realm_req: str, level_req: int,
    shield: float = 0.0, reflect: float = 0.0
) -> Skill:
    """创建防御功法"""
    effects = [SkillEffect(
        effect_type="defense",
        base_value=defense,
        per_level=defense * 0.1,
        description=f"防御力+{defense}"
    )]
    
    if shield > 0:
        effects.append(SkillEffect(
            effect_type="shield",
            base_value=shield,
            per_level=shield * 0.1,
            description=f"护盾 +{shield}"
        ))
    if reflect > 0:
        effects.append(SkillEffect(
            effect_type="reflect",
            base_value=reflect,
            per_level=reflect * 0.05,
            description=f"反伤 {reflect*100}%"
        ))
    
    return Skill(
        id=skill_id,
        name=name,
        type=SkillType.DEFENSE,
        element=element,
        grade=grade,
        description=description,
        requirement_realm=realm_req,
        requirement_level=level_req,
        qi_cost=qi_cost,
        cooldown=cooldown,
        effects=effects
    )


def _create_support_skill(
    skill_id: str, name: str, element: SkillElement, grade: SkillGrade,
    qi_cost: float, cooldown: int, description: str,
    realm_req: str, level_req: int,
    heal: float = 0.0, regen: float = 0.0, buff: str = "", buff_value: float = 0.0, buff_duration: int = 0
) -> Skill:
    """创建辅助功法"""
    effects = []
    
    if heal > 0:
        effects.append(SkillEffect(
            effect_type="heal",
            base_value=heal,
            per_level=heal * 0.15,
            description=f"恢复 {heal} 生命"
        ))
    if regen > 0:
        effects.append(SkillEffect(
            effect_type="regen",
            base_value=regen,
            per_level=regen * 0.1,
            description=f"持续恢复 {regen} 生命/回合"
        ))
    if buff:
        effects.append(SkillEffect(
            effect_type="buff",
            base_value=buff_value,
            per_level=buff_value * 0.1,
            description=f"{buff} +{buff_value*100}%"
        ))
    
    return Skill(
        id=skill_id,
        name=name,
        type=SkillType.SUPPORT,
        element=element,
        grade=grade,
        description=description,
        requirement_realm=realm_req,
        requirement_level=level_req,
        qi_cost=qi_cost,
        cooldown=cooldown,
        effects=effects,
        special_effects={"buff": buff, "buff_value": buff_value, "buff_duration": buff_duration}
    )


def _create_debuff_skill(
    skill_id: str, name: str, element: SkillElement, grade: SkillGrade,
    attack: float, qi_cost: float, cooldown: int, description: str,
    realm_req: str, level_req: int,
    debuff: str = "", debuff_value: float = 0.0, debuff_duration: int = 0,
    dot: float = 0.0
) -> Skill:
    """创建减益功法"""
    effects = []
    
    if attack > 0:
        effects.append(SkillEffect(
            effect_type="attack",
            base_value=attack,
            per_level=attack * 0.15,
            description=f"造成 {attack} 点伤害"
        ))
    if dot > 0:
        effects.append(SkillEffect(
            effect_type="dot",
            base_value=dot,
            per_level=dot * 0.1,
            description=f"每回合 {dot} 伤害"
        ))
    
    return Skill(
        id=skill_id,
        name=name,
        type=SkillType.ATTACK,
        element=element,
        grade=grade,
        description=description,
        requirement_realm=realm_req,
        requirement_level=level_req,
        qi_cost=qi_cost,
        cooldown=cooldown,
        effects=effects,
        special_effects={"debuff": debuff, "debuff_value": debuff_value, "debuff_duration": debuff_duration}
    )


SKILLS_DATABASE: Dict[str, Skill] = {
    # ============ 修炼功法 ============
    "intro_cultivation": _create_cultivation_skill(
        "intro_cultivation", "引气诀", SkillElement.WOOD, SkillGrade.MORTAL,
        0.2, "最基础的修炼法门，适合初学者", "炼气期", 1
    ),
    "fire_cultivation": _create_cultivation_skill(
        "fire_cultivation", "烈焰心法", SkillElement.FIRE, SkillGrade.SPIRIT,
        0.4, "火属性修炼心法，灵气更为猛烈", "炼气期", 3
    ),
    "water_cultivation": _create_cultivation_skill(
        "water_cultivation", "流水心经", SkillElement.WATER, SkillGrade.SPIRIT,
        0.4, "水属性修炼心法，灵气更为绵长", "炼气期", 3
    ),
    "metal_cultivation": _create_cultivation_skill(
        "metal_cultivation", "金精决", SkillElement.METAL, SkillGrade.SPIRIT,
        0.45, "金属性修炼心法，灵气锋锐", "炼气期", 5
    ),
    "earth_cultivation": _create_cultivation_skill(
        "earth_cultivation", "厚土功", SkillElement.EARTH, SkillGrade.SPIRIT,
        0.45, "土属性修炼心法，根基稳固", "炼气期", 5
    ),
    "thunder_cultivation": _create_cultivation_skill(
        "thunder_cultivation", "奔雷诀", SkillElement.THUNDER, SkillGrade.DIVINE,
        0.6, "雷属性天品心法，修炼速度极快", "筑基期", 1
    ),
    "ice_cultivation": _create_cultivation_skill(
        "ice_cultivation", "冰心诀", SkillElement.ICE, SkillGrade.DIVINE,
        0.6, "冰属性天品心法，心境清明", "筑基期", 1
    ),
    
    # ============ 攻击功法 - 单体 ============
    "fireball": _create_attack_skill(
        "fireball", "火球术", SkillElement.FIRE, SkillGrade.MORTAL,
        15, 15, 1, "释放一个炽热的火球攻击敌人", "炼气期", 1
    ),
    "ice_shard": _create_attack_skill(
        "ice_shard", "冰锥术", SkillElement.ICE, SkillGrade.MORTAL,
        12, 12, 1, "发射尖锐的冰锥", "炼气期", 1
    ),
    "metal_slice": _create_attack_skill(
        "metal_slice", "金刃斩", SkillElement.METAL, SkillGrade.MORTAL,
        14, 14, 1, "金属性切割术", "炼气期", 2
    ),
    "thunder_strike": _create_attack_skill(
        "thunder_strike", "天雷击", SkillElement.THUNDER, SkillGrade.SPIRIT,
        30, 25, 2, "召唤天雷攻击敌人", "炼气期", 5
    ),
    "water_splash": _create_attack_skill(
        "water_splash", "水波术", SkillElement.WATER, SkillGrade.SPIRIT,
        25, 20, 1, "水波冲击", "炼气期", 4
    ),
    "wind_blade": _create_attack_skill(
        "wind_blade", "风刃", SkillElement.WIND, SkillGrade.SPIRIT,
        28, 22, 1, "高速风刃切割", "炼气期", 4
    ),
    "earth_collapse": _create_attack_skill(
        "earth_collapse", "崩土术", SkillElement.EARTH, SkillGrade.SPIRIT,
        32, 28, 2, "大地崩裂攻击", "筑基期", 1
    ),
    "inferno": _create_attack_skill(
        "inferno", "烈焰风暴", SkillElement.FIRE, SkillGrade.DIVINE,
        60, 50, 3, "召唤烈焰风暴", "筑基期", 5
    ),
    "thunder_rain": _create_attack_skill(
        "thunder_rain", "万雷天降", SkillElement.THUNDER, SkillGrade.CELESTIAL,
        100, 80, 4, "召唤万千雷电", "金丹期", 1
    ),
    
    # ============ 攻击功法 - 连击系 ============
    "double_strike": _create_attack_skill(
        "double_strike", "连击", SkillElement.NONE, SkillGrade.MORTAL,
        20, 20, 2, "快速连击两次", "炼气期", 2,
        hits=2
    ),
    "triple_blade": _create_attack_skill(
        "triple_blade", "三刃斩", SkillElement.METAL, SkillGrade.SPIRIT,
        35, 30, 2, "三重刀刃斩击", "炼气期", 4,
        hits=3
    ),
    "rain_blade": _create_attack_skill(
        "rain_blade", "暴雨剑", SkillElement.WATER, SkillGrade.DIVINE,
        50, 45, 3, "如暴雨般的剑击", "筑基期", 3,
        hits=5
    ),
    "thousand_swords": _create_attack_skill(
        "thousand_swords", "万剑诀", SkillElement.METAL, SkillGrade.CELESTIAL,
        80, 70, 4, "万剑齐发", "金丹期", 3,
        hits=8
    ),
    
    # ============ 攻击功法 - 吸血系 ============
    "vampire_touch": _create_attack_skill(
        "vampire_touch", "吸血大法", SkillElement.DARKNESS, SkillGrade.SPIRIT,
        20, 25, 3, "攻击敌人并吸取生命", "炼气期", 5,
        lifesteal=0.3
    ),
    "demon_siphon": _create_attack_skill(
        "demon_siphon", "魔婴吸元", SkillElement.DARKNESS, SkillGrade.DIVINE,
        45, 40, 3, "恶魔般的吸血能力", "筑基期", 4,
        lifesteal=0.5
    ),
    "soul_drain": _create_attack_skill(
        "soul_drain", "抽魂夺魄", SkillElement.DARKNESS, SkillGrade.CELESTIAL,
        70, 60, 4, "吸取敌人灵魂", "金丹期", 2,
        lifesteal=0.7
    ),
    
    # ============ 攻击功法 - 真实伤害 ============
    "true_strike": _create_attack_skill(
        "true_strike", "破甲击", SkillElement.NONE, SkillGrade.SPIRIT,
        10, 20, 2, "无视防御的真实伤害", "炼气期", 3,
        true_damage=20
    ),
    "void_tear": _create_attack_skill(
        "void_tear", "虚空撕裂", SkillElement.DARKNESS, SkillGrade.DIVINE,
        30, 40, 3, "撕裂空间造成真实伤害", "筑基期", 3,
        true_damage=50
    ),
    "heaven_slice": _create_attack_skill(
        "heaven_slice", "斩天剑", SkillElement.LIGHT, SkillGrade.CELESTIAL,
        50, 80, 4, "天道之剑，无视防御", "金丹期", 2,
        true_damage=100
    ),
    
    # ============ 攻击功法 - 减益系 (DOT) ============
    "poison_cloud": _create_debuff_skill(
        "poison_cloud", "毒云术", SkillElement.WOOD, SkillGrade.SPIRIT,
        15, 25, 2, "释放毒云", "炼气期", 4,
        debuff="poison", debuff_value=5.0, debuff_duration=3,
        dot=5.0
    ),
    "hellfire": _create_debuff_skill(
        "hellfire", "地狱火", SkillElement.FIRE, SkillGrade.DIVINE,
        40, 45, 3, "地狱烈焰灼烧", "筑基期", 4,
        debuff="burn", debuff_value=10.0, debuff_duration=3,
        dot=10.0
    ),
    "cursed_needle": _create_debuff_skill(
        "cursed_needle", "噬魂钉", SkillElement.DARKNESS, SkillGrade.CELESTIAL,
        60, 60, 4, "诅咒之钉，造成持续伤害", "金丹期", 3,
        debuff="bleed", debuff_value=15.0, debuff_duration=4,
        dot=15.0
    ),
    
    # ============ 防御功法 ============
    "stone_skin": _create_defense_skill(
        "stone_skin", "石肤术", SkillElement.EARTH, SkillGrade.MORTAL,
        10, 10, 2, "皮肤如岩石般坚硬", "炼气期", 1
    ),
    "water_shield": _create_defense_skill(
        "water_shield", "水盾", SkillElement.WATER, SkillGrade.MORTAL,
        8, 12, 2, "用水元素形成护盾", "炼气期", 2,
        shield=30
    ),
    "fire_wall": _create_defense_skill(
        "fire_wall", "火墙", SkillElement.FIRE, SkillGrade.SPIRIT,
        20, 20, 3, "召唤一道火墙", "炼气期", 4,
        shield=50
    ),
    "thunder_shield": _create_defense_skill(
        "thunder_shield", "雷盾", SkillElement.THUNDER, SkillGrade.DIVINE,
        35, 30, 3, "雷电形成的护盾", "筑基期", 3,
        shield=80
    ),
    "ice_armor": _create_defense_skill(
        "ice_armor", "冰甲", SkillElement.ICE, SkillGrade.DIVINE,
        40, 35, 3, "寒冰铠甲", "筑基期", 4,
        shield=100
    ),
    "diamond_body": _create_defense_skill(
        "diamond_body", "金刚不坏", SkillElement.METAL, SkillGrade.CELESTIAL,
        60, 60, 4, "无上防御神通", "金丹期", 2,
        shield=200
    ),
    
    # ============ 防御功法 - 反伤系 ============
    "thorn_armor": _create_defense_skill(
        "thorn_armor", "荆棘甲", SkillElement.WOOD, SkillGrade.SPIRIT,
        15, 25, 3, "攻击者受到反伤", "炼气期", 5,
        reflect=0.3
    ),
    "hell_flames": _create_defense_skill(
        "hell_flames", "炼狱火", SkillElement.FIRE, SkillGrade.DIVINE,
        30, 40, 3, "灼烧近战攻击者", "筑基期", 4,
        reflect=0.5
    ),
    
    # ============ 辅助功法 - 治疗 ============
    "heal": _create_support_skill(
        "heal", "治疗术", SkillElement.LIGHT, SkillGrade.SPIRIT,
        25, 3, "恢复自身或队友的生命", "炼气期", 3,
        heal=30
    ),
    "greater_heal": _create_support_skill(
        "greater_heal", "大治疗术", SkillElement.LIGHT, SkillGrade.DIVINE,
        40, 4, "大量恢复生命", "筑基期", 3,
        heal=80
    ),
    "rejuvenation": _create_support_skill(
        "rejuvenation", "生机术", SkillElement.WOOD, SkillGrade.DIVINE,
        35, 4, "持续恢复生命", "筑基期", 4,
        regen=15, buff="regen", buff_value=0.1, buff_duration=3
    ),
    "divine_heal": _create_support_skill(
        "divine_heal", "圣光普照", SkillElement.LIGHT, SkillGrade.CELESTIAL,
        60, 5, "神圣治疗", "金丹期", 2,
        heal=150
    ),
    
    # ============ 辅助功法 - 增益 ============
    "swift_foot": _create_support_skill(
        "swift_foot", "轻身术", SkillElement.WIND, SkillGrade.MORTAL,
        10, 5, "提升移动速度和闪避", "炼气期", 2,
        buff="speed", buff_value=0.2, buff_duration=3
    ),
    "battle_fury": _create_support_skill(
        "battle_fury", "战意", SkillElement.FIRE, SkillGrade.SPIRIT,
        25, 4, "提升攻击力", "炼气期", 4,
        buff="attack", buff_value=0.3, buff_duration=3
    ),
    "divine_protection": _create_support_skill(
        "divine_protection", "神圣祝福", SkillElement.LIGHT, SkillGrade.DIVINE,
        40, 5, "全属性提升", "筑基期", 3,
        buff="all", buff_value=0.2, buff_duration=3
    ),
    " berserker": _create_support_skill(
        "berserker", "狂化", SkillElement.FIRE, SkillGrade.CELESTIAL,
        50, 6, "牺牲防御换取极致攻击", "金丹期", 2,
        buff="attack", buff_value=0.5, buff_duration=2
    ),
    
    # ============ 辅助功法 - 灵气恢复 ============
    "qi_flow": _create_support_skill(
        "qi_flow", "灵气流转", SkillElement.WATER, SkillGrade.SPIRIT,
        0, 4, "恢复灵气", "炼气期", 3,
        heal=0, regen=0
    ),
    "spirit_gather": _create_support_skill(
        "spirit_gather", "聚灵术", SkillElement.WATER, SkillGrade.DIVINE,
        0, 5, "大量恢复灵气", "筑基期", 3,
        heal=0, regen=0
    ),
    
    # ============ 特殊功法 ============
    "counter_strike": Skill(
        id="counter_strike",
        name="反击",
        type=SkillType.SPECIAL,
        element=SkillElement.NONE,
        grade=SkillGrade.SPIRIT,
        description="受到攻击时自动反击",
        requirement_realm="炼气期",
        requirement_level=5,
        qi_cost=30,
        cooldown=5,
        effects=[SkillEffect(
            effect_type="counter",
            base_value=0.5,
            per_level=0.1,
            description="反击概率50%"
        )]
    ),
    "absolute_defense": Skill(
        id="absolute_defense",
        name="绝对防御",
        type=SkillType.SPECIAL,
        element=SkillElement.LIGHT,
        grade=SkillGrade.CELESTIAL,
        description="一段时间内免疫所有伤害",
        requirement_realm="金丹期",
        requirement_level=2,
        qi_cost=100,
        cooldown=8,
        effects=[SkillEffect(
            effect_type="invincible",
            base_value=2,
            per_level=1,
            description="无敌2回合"
        )]
    ),
    
    # ============ 被动功法 ============
    "metal_body": Skill(
        id="metal_body",
        name="金身",
        type=SkillType.PASSIVE,
        element=SkillElement.METAL,
        grade=SkillGrade.DIVINE,
        description="金属性体质，被动提升防御",
        requirement_realm="筑基期",
        requirement_level=3,
        passive_effects={"defense": 20, "attack": 10}
    ),
    "fire_body": Skill(
        id="fire_body",
        name="火体",
        type=SkillType.PASSIVE,
        element=SkillElement.FIRE,
        grade=SkillGrade.DIVINE,
        description="火属性体质，被动提升攻击",
        requirement_realm="筑基期",
        requirement_level=3,
        passive_effects={"attack": 25, "crit": 0.1}
    ),
    "thunder_body": Skill(
        id="thunder_body",
        name="雷体",
        type=SkillType.PASSIVE,
        element=SkillElement.THUNDER,
        grade=SkillGrade.CELESTIAL,
        description="雷属性天品体质，大幅提升攻击和暴击",
        requirement_realm="金丹期",
        requirement_level=1,
        passive_effects={"attack": 40, "crit": 0.2}
    ),
    "water_body": Skill(
        id="water_body",
        name="水灵体",
        type=SkillType.PASSIVE,
        element=SkillElement.WATER,
        grade=SkillGrade.DIVINE,
        description="水属性体质，灵气恢复速度提升",
        requirement_realm="筑基期",
        requirement_level=2,
        passive_effects={"defense": 15, "speed": 0.1}
    ),
    "immortal_body": Skill(
        id="immortal_body",
        name="不灭金身",
        type=SkillType.PASSIVE,
        element=SkillElement.LIGHT,
        grade=SkillGrade.CELESTIAL,
        description="仙人资质，所有属性大幅提升",
        requirement_realm="金丹期",
        requirement_level=3,
        passive_effects={"attack": 60, "defense": 40, "crit": 0.15, "max_hp": 0.3}
    ),
}


# ============ 功法系统 ============

class SkillSystem:
    """功法系统"""
    
    @staticmethod
    def can_learn(player, skill_id: str) -> tuple:
        """
        检查是否可以学习功法
        返回 (can_learn: bool, reason: str)
        """
        skill = SKILLS_DATABASE.get(skill_id)
        if not skill:
            return False, "功法不存在"
        
        if skill_id in player.skills:
            return False, "已学会此功法"
        
        # 检查境界要求
        realm_order = ["凡人", "炼气期", "筑基期", "金丹期", "元婴期", "化神期"]
        player_realm_idx = realm_order.index(player.realm.value) if player.realm.value in realm_order else 0
        req_realm_idx = realm_order.index(skill.requirement_realm) if skill.requirement_realm in realm_order else 0
        
        if player_realm_idx < req_realm_idx:
            return False, f"需要{skill.requirement_realm}"
        
        if player_realm_idx == req_realm_idx and player.level < skill.requirement_level:
            return False, f"需要{skill.requirement_realm}第{skill.requirement_level}层"
        
        # 检查灵石
        cost = skill.grade.stars * 50
        if player.spirit_stones < cost:
            return False, f"需要{cost}灵石"
        
        return True, ""
    
    @staticmethod
    def learn_skill(player, skill_id: str) -> tuple:
        """
        学习功法
        返回 (success: bool, message: str)
        """
        can_learn, reason = SkillSystem.can_learn(player, skill_id)
        if not can_learn:
            return False, reason
        
        skill = SKILLS_DATABASE[skill_id]
        
        # 扣除灵石
        cost = skill.grade.stars * 50
        player.spirit_stones -= cost
        
        # 添加功法
        player.skills[skill_id] = PlayerSkill(skill_id=skill_id, level=1)
        
        # 应用被动效果
        for attr, value in skill.passive_effects.items():
            if hasattr(player, attr):
                setattr(player, attr, getattr(player, attr) + value)
        
        # 更新修炼速度
        player.cultivation_speed = SkillSystem.get_cultivation_bonus(player)
        
        return True, f"成功学会【{skill.name}】！消耗{cost}灵石"
    
    @staticmethod
    def upgrade_skill(player, skill_id: str) -> tuple:
        """
        升级功法
        返回 (success: bool, message: str)
        """
        if skill_id not in player.skills:
            return False, "未学会此功法"
        
        player_skill = player.skills[skill_id]
        skill = SKILLS_DATABASE.get(skill_id)
        
        if not skill:
            return False, "功法不存在"
        
        if player_skill.is_max_level:
            return False, "功法已满级"
        
        # 检查经验
        exp_needed = player_skill.exp_needed
        if player_skill.exp < exp_needed:
            return False, f"需要{exp_needed}熟练度，当前{player_skill.exp}"
        
        # 升级
        player_skill.add_exp(0)  # 触发升级检查
        return True, f"【{skill.name}】升级到第{player_skill.level}层！"
    
    @staticmethod
    def get_skill_info(skill_id: str) -> Optional[Skill]:
        """获取功法信息"""
        return SKILLS_DATABASE.get(skill_id)
    
    @staticmethod
    def get_available_skills(player) -> List[Skill]:
        """获取可学习的功法列表"""
        available = []
        for skill_id, skill in SKILLS_DATABASE.items():
            if skill_id not in player.skills:
                can_learn, _ = SkillSystem.can_learn(player, skill_id)
                if can_learn:
                    available.append(skill)
        return available
    
    @staticmethod
    def get_learned_skills(player) -> List[PlayerSkill]:
        """获取已学功法列表"""
        return list(player.skills.values())
    
    @staticmethod
    def get_cultivation_bonus(player) -> float:
        """计算修炼加成"""
        bonus = 1.0
        
        for skill_id, player_skill in player.skills.items():
            skill = SKILLS_DATABASE.get(skill_id)
            if skill and skill.type == SkillType.CULTIVATION:
                # 基础加成
                cultivation_effect = skill.get_effect_value("cultivation", player_skill.level)
                bonus += cultivation_effect
        
        # 灵根加成
        if player.elements:
            from core.element import ElementSystem
            synergy = ElementSystem.calculate_element_synergy(player.elements)
            bonus *= synergy.get("cultivation", 1.0)
        
        return bonus
    
    @staticmethod
    def use_skill(skill_id: str, player, target=None) -> dict:
        """
        使用功法
        返回使用结果
        """
        if skill_id not in player.skills:
            return {"success": False, "message": "未学会此功法"}
        
        skill = SKILLS_DATABASE.get(skill_id)
        if not skill:
            return {"success": False, "message": "功法不存在"}
        
        player_skill = player.skills[skill_id]
        
        # 检查冷却
        if hasattr(player, 'cooldowns') and skill_id in player.cooldowns:
            if player.cooldowns[skill_id] > 0:
                return {"success": False, "message": f"技能冷却中，{player.cooldowns[skill_id]}回合后可用"}
        
        # 检查灵气
        if not player.consume_qi(skill.qi_cost):
            return {"success": False, "message": "灵气不足"}
        
        # 计算效果
        element_match = 1.0
        if player.elements and skill.element != SkillElement.NONE:
            from core.element import ElementType, Element
            for elem in player.elements:
                if elem.type.name == skill.element.name:
                    element_match = 1.2  # 元素契合加成
                    break
        
        result = {
            "success": True,
            "skill_name": skill.name,
            "damage": 0,
            "heal": 0,
            "defense": 0,
            "message": f"使用【{skill.name}】"
        }
        
        # 应用效果
        for effect in skill.effects:
            value = effect.calculate(player_skill.level, element_match)
            
            if effect.effect_type == "attack":
                result["damage"] = int(value)
            elif effect.effect_type == "heal":
                result["heal"] = int(value)
            elif effect.effect_type == "defense":
                result["defense"] = int(value)
            elif effect.effect_type == "shield":
                result["shield"] = int(value)
            elif effect.effect_type == "lifesteal":
                result["lifesteal"] = value
            elif effect.effect_type == "regen":
                result["regen"] = int(value)
            elif effect.effect_type == "true_damage":
                result["true_damage"] = int(value)
            elif effect.effect_type == "hits":
                result["hits"] = int(value)
            elif effect.effect_type == "dot":
                result["dot"] = int(value)
            elif effect.effect_type == "buff":
                result["buff"] = skill.special_effects.get("buff", "")
                result["buff_value"] = value
                result["buff_duration"] = skill.special_effects.get("buff_duration", 2)
        
        # 应用特殊效果
        if skill.special_effects:
            if "buff" in skill.special_effects and skill.special_effects["buff"]:
                result["buff"] = skill.special_effects["buff"]
                result["buff_value"] = skill.special_effects.get("buff_value", 0.1)
                result["buff_duration"] = skill.special_effects.get("buff_duration", 2)
            if "debuff" in skill.special_effects and skill.special_effects["debuff"]:
                result["debuff"] = skill.special_effects["debuff"]
                result["debuff_value"] = skill.special_effects.get("debuff_value", 0.1)
                result["debuff_duration"] = skill.special_effects.get("debuff_duration", 2)
        
        # 设置冷却
        if skill.cooldown > 0:
            if not hasattr(player, 'cooldowns'):
                player.cooldowns = {}
            player.cooldowns[skill_id] = skill.cooldown
        
        return result
    
    @staticmethod
    def list_all_skills() -> List[Skill]:
        """列出所有功法"""
        return list(SKILLS_DATABASE.values())
    
    @staticmethod
    def list_skills_by_type(skill_type: SkillType) -> List[Skill]:
        """按类型列出功法"""
        return [s for s in SKILLS_DATABASE.values() if s.type == skill_type]
