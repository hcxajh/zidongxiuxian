"""
修仙游戏 - 灵根系统
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import random


class ElementType(Enum):
    """灵根元素类型"""
    # 五行
    METAL = "金"
    WOOD = "木"
    WATER = "水"
    FIRE = "火"
    EARTH = "土"
    # 变异
    THUNDER = "雷"
    ICE = "冰"
    WIND = "风"
    LIGHT = "光"
    DARKNESS = "暗"


# 灵根属性加成配置
ELEMENT_ATTACK_BONUS = {
    ElementType.METAL: {"attack": 1.2, "defense": 1.1},
    ElementType.WOOD: {"attack": 1.1, "cultivation": 1.2},
    ElementType.WATER: {"attack": 1.1, "defense": 1.2},
    ElementType.FIRE: {"attack": 1.3, "crit": 0.1},
    ElementType.EARTH: {"defense": 1.3, "hp": 1.2},
    ElementType.THUNDER: {"attack": 1.4, "crit": 0.15},
    ElementType.ICE: {"attack": 1.2, "defense": 1.1},
    ElementType.WIND: {"speed": 1.3, "attack": 1.15},
    ElementType.LIGHT: {"attack": 1.25, "cultivation": 1.15},
    ElementType.DARKNESS: {"attack": 1.3, "defense": 1.1},
}

# 相生关系 (增强)
ELEMENT_AUGMENTS = {
    ElementType.METAL: ElementType.WATER,   # 金生水
    ElementType.WOOD: ElementType.FIRE,    # 木生火
    ElementType.WATER: ElementType.WOOD,   # 水生木
    ElementType.FIRE: ElementType.EARTH,   # 火生土
    ElementType.EARTH: ElementType.METAL,  # 土生金
}

# 相克关系 (克制)
ELEMENT_WEAKNESS = {
    ElementType.METAL: ElementType.FIRE,
    ElementType.WOOD: ElementType.METAL,
    ElementType.WATER: ElementType.EARTH,
    ElementType.FIRE: ElementType.WATER,
    ElementType.EARTH: ElementType.WOOD,
    ElementType.THUNDER: ElementType.ICE,
    ElementType.ICE: ElementType.FIRE,
    ElementType.WIND: ElementType.EARTH,
    ElementType.LIGHT: ElementType.DARKNESS,
    ElementType.DARKNESS: ElementType.LIGHT,
}


@dataclass
class Element:
    """灵根"""
    type: ElementType
    grade: int = 1  # 灵根等级 (1-10, 天灵根为10)
    
    @property
    def name(self) -> str:
        """灵根名称"""
        grade_names = {
            10: "天灵根",
            9: "真灵根",
            7: "异灵根",
            5: "杂灵根",
            1: "伪灵根",
        }
        grade_name = grade_names.get(self.grade, "凡品")
        return f"{self.type.value}{grade_name}"
    
    @property
    def attack_multiplier(self) -> float:
        """攻击倍率"""
        return ELEMENT_ATTACK_BONUS.get(self.type, {}).get("attack", 1.0)
    
    @property
    def defense_multiplier(self) -> float:
        """防御倍率"""
        return ELEMENT_ATTACK_BONUS.get(self.type, {}).get("defense", 1.0)
    
    @property
    def cultivation_multiplier(self) -> float:
        """修炼速度倍率"""
        base = ELEMENT_ATTACK_BONUS.get(self.type, {}).get("cultivation", 1.0)
        # 天灵根额外加成
        if self.grade >= 9:
            base *= 1.5
        elif self.grade >= 7:
            base *= 1.3
        return base
    
    @property
    def crit_bonus(self) -> float:
        """暴击加成"""
        return ELEMENT_ATTACK_BONUS.get(self.type, {}).get("crit", 0.0)


@dataclass
class ElementSystem:
    """灵根系统"""
    
    @staticmethod
    def generate_random_element(grade_range: tuple = (3, 7)) -> Element:
        """随机生成灵根"""
        all_types = list(ElementType)
        element_type = random.choice(all_types)
        grade = random.randint(*grade_range)
        return Element(type=element_type, grade=grade)
    
    @staticmethod
    def generate_player_elements(count: int = 1, grade_range: tuple = (3, 7)) -> List[Element]:
        """生成玩家灵根"""
        elements = []
        available_types = list(ElementType)
        
        for _ in range(count):
            if not available_types:
                break
            element_type = random.choice(available_types)
            available_types.remove(element_type)
            grade = random.randint(*grade_range)
            elements.append(Element(type=element_type, grade=grade))
        
        return elements
    
    @staticmethod
    def calculate_element_synergy(elements: List[Element]) -> Dict[str, float]:
        """计算灵根协同效果"""
        if not elements:
            return {"attack": 1.0, "defense": 1.0, "cultivation": 1.0}
        
        result = {
            "attack": 1.0,
            "defense": 1.0,
            "cultivation": 1.0,
            "crit": 0.0,
            "speed": 1.0,
            "hp": 1.0,
        }
        
        for elem in elements:
            result["attack"] *= elem.attack_multiplier
            result["defense"] *= elem.defense_multiplier
            result["cultivation"] *= elem.cultivation_multiplier
            result["crit"] += elem.crit_bonus
        
        # 多灵根额外加成
        if len(elements) >= 3:
            result["cultivation"] *= 1.2  # 三灵根以上修炼更快
            result["attack"] *= 1.1
        
        return result
    
    @staticmethod
    def get_element_advantage(attack_elem: ElementType, defense_elem: ElementType) -> float:
        """获取元素克制倍率"""
        if ELEMENT_WEAKNESS.get(attack_elem) == defense_elem:
            return 1.5  # 克制
        if ELEMENT_WEAKNESS.get(defense_elem) == attack_elem:
            return 0.7  # 被克制
        return 1.0
    
    @staticmethod
    def get_augment_bonus(elements: List[Element]) -> float:
        """获取相生加成"""
        if len(elements) < 2:
            return 1.0
        
        bonus = 1.0
        for i, elem in enumerate(elements):
            if i + 1 < len(elements):
                next_elem = elements[i + 1]
                if ELEMENT_AUGMENTS.get(elem.type) == next_elem.type:
                    bonus *= 1.15
        return bonus


# 灵根品质生成概率
ELEMENT_GRADE_CHANCE = {
    10: 0.01,   # 天灵根 1%
    9: 0.04,    # 真灵根 4%
    8: 0.10,    # 精品 10%
    7: 0.20,    # 异灵根 20%
    6: 0.25,    # 25%
    5: 0.25,    # 25%
    4: 0.10,    # 10%
    3: 0.04,    # 4%
    2: 0.01,    # 1%
    1: 0.00,    # 不可能出现
}


def generate_element_with_grade(target_grade: int) -> Element:
    """根据目标等级生成灵根"""
    # 尝试生成指定等级的灵根
    for _ in range(100):
        all_types = list(ElementType)
        element_type = random.choice(all_types)
        
        # 根据概率生成等级
        rand = random.random()
        cumulative = 0
        actual_grade = 5
        for grade, chance in ELEMENT_GRADE_CHANCE.items():
            cumulative += chance
            if rand <= cumulative:
                actual_grade = grade
                break
        
        if actual_grade == target_grade:
            return Element(type=element_type, grade=actual_grade)
    
    # 兜底
    return Element(type=random.choice(list(ElementType)), grade=target_grade)
