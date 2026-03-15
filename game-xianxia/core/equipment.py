"""
修仙游戏 - 装备系统
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import random


class EquipmentType(Enum):
    """装备类型"""
    WEAPON = "武器"
    ARMOR = "防具"
    HELMET = "头盔"
    BOOTS = "靴子"
    RING = "戒指"
    AMULET = "项链"
    BELT = "腰带"


class EquipmentQuality(Enum):
    """装备品质"""
    MORTAL = ("凡品", 1, 1.0)
    SPIRIT = ("灵品", 2, 1.5)
    DIVINE = ("神品", 3, 2.5)
    CELESTIAL = ("天品", 4, 4.0)
    IMMORTAL = ("仙品", 5, 8.0)
    
    def __init__(self, quality_name: str, stars: int, multiplier: float):
        self.quality_name = quality_name
        self.stars = stars
        self.multiplier = multiplier
    
    @property
    def name(self) -> str:
        return self.quality_name


class EquipmentSlot(Enum):
    """装备槽位"""
    WEAPON = "weapon"
    ARMOR = "armor"
    HELMET = "helmet"
    BOOTS = "boots"
    RING1 = "ring1"
    RING2 = "ring2"
    AMULET = "amulet"
    BELT = "belt"
    
    @property
    def equipment_type(self) -> EquipmentType:
        """槽位对应的装备类型"""
        mapping = {
            EquipmentSlot.WEAPON: EquipmentType.WEAPON,
            EquipmentSlot.ARMOR: EquipmentType.ARMOR,
            EquipmentSlot.HELMET: EquipmentType.HELMET,
            EquipmentSlot.BOOTS: EquipmentType.BOOTS,
            EquipmentSlot.RING1: EquipmentType.RING,
            EquipmentSlot.RING2: EquipmentType.RING,
            EquipmentSlot.AMULET: EquipmentType.AMULET,
            EquipmentSlot.BELT: EquipmentType.BELT,
        }
        return mapping.get(self, EquipmentType.WEAPON)


@dataclass
class EquipmentStats:
    """装备属性"""
    attack: int = 0
    defense: int = 0
    hp: int = 0
    qi: int = 0
    crit: float = 0.0
    crit_damage: float = 0.0
    speed: float = 0.0
    cultivation_speed: float = 0.0
    elemental_attack: Dict[str, int] = field(default_factory=dict)  # 元素攻击
    elemental_defense: Dict[str, int] = field(default_factory=dict)  # 元素防御
    
    def add(self, other: 'EquipmentStats') -> 'EquipmentStats':
        """合并属性"""
        result = EquipmentStats()
        result.attack = self.attack + other.attack
        result.defense = self.defense + other.defense
        result.hp = self.hp + other.hp
        result.qi = self.qi + other.qi
        result.crit = self.crit + other.crit
        result.crit_damage = self.crit_damage + other.crit_damage
        result.speed = self.speed + other.speed
        result.cultivation_speed = self.cultivation_speed + other.cultivation_speed
        
        # 合并元素属性
        for elem, val in self.elemental_attack.items():
            result.elemental_attack[elem] = result.elemental_attack.get(elem, 0) + val
        for elem, val in other.elemental_attack.items():
            result.elemental_attack[elem] = result.elemental_attack.get(elem, 0) + val
            
        for elem, val in self.elemental_defense.items():
            result.elemental_defense[elem] = result.elemental_defense.get(elem, 0) + val
        for elem, val in other.elemental_defense.items():
            result.elemental_defense[elem] = result.elemental_defense.get(elem, 0) + val
            
        return result
    
    def multiply(self, multiplier: float) -> 'EquipmentStats':
        """属性乘算"""
        result = EquipmentStats()
        result.attack = int(self.attack * multiplier)
        result.defense = int(self.defense * multiplier)
        result.hp = int(self.hp * multiplier)
        result.qi = int(self.qi * multiplier)
        result.crit = self.crit * multiplier
        result.crit_damage = self.crit_damage * multiplier
        result.speed = self.speed * multiplier
        result.cultivation_speed = self.cultivation_speed * multiplier
        result.elemental_attack = {k: int(v * multiplier) for k, v in self.elemental_attack.items()}
        result.elemental_defense = {k: int(v * multiplier) for k, v in self.elemental_defense.items()}
        return result
    
    def to_dict(self) -> dict:
        """转为字典"""
        result = {}
        if self.attack:
            result["attack"] = self.attack
        if self.defense:
            result["defense"] = self.defense
        if self.hp:
            result["hp"] = self.hp
        if self.qi:
            result["qi"] = self.qi
        if self.crit:
            result["crit"] = f"+{self.crit*100:.0f}%"
        if self.crit_damage:
            result["crit_damage"] = f"+{self.crit_damage*100:.0f}%"
        if self.speed:
            result["speed"] = f"+{self.speed:.1f}"
        if self.cultivation_speed:
            result["cultivation_speed"] = f"+{self.cultivation_speed*100:.0f}%"
        for elem, val in self.elemental_attack.items():
            result[f"{elem}_attack"] = val
        for elem, val in self.elemental_defense.items():
            result[f"{elem}_defense"] = val
        return result


@dataclass
class Equipment:
    """装备"""
    id: str
    name: str
    type: EquipmentType
    quality: EquipmentQuality
    level_required: int = 1
    
    # 基础属性
    base_stats: EquipmentStats = field(default_factory=EquipmentStats)
    
    # 强化属性
    enhancement_level: int = 0
    enhancement_bonus: float = 0.0  # 强化加成
    
    # 描述
    description: str = ""
    element: str = ""  # 元素属性
    
    # 稀有属性（随机生成）
    rare_stats: EquipmentStats = field(default_factory=EquipmentStats)
    
    @property
    def total_stats(self) -> EquipmentStats:
        """总属性 = 基础 * 品质倍率 * 强化加成 + 稀有属性"""
        enhanced = self.base_stats.multiply(self.quality.multiplier * (1 + self.enhancement_bonus))
        return enhanced.add(self.rare_stats)
    
    @property
    def slot(self) -> EquipmentSlot:
        """装备槽位"""
        mapping = {
            EquipmentType.WEAPON: EquipmentSlot.WEAPON,
            EquipmentType.ARMOR: EquipmentSlot.ARMOR,
            EquipmentType.HELMET: EquipmentSlot.HELMET,
            EquipmentType.BOOTS: EquipmentSlot.BOOTS,
            EquipmentType.RING: EquipmentSlot.RING1,
            EquipmentType.AMULET: EquipmentSlot.AMULET,
            EquipmentType.BELT: EquipmentSlot.BELT,
        }
        return mapping.get(self.type, EquipmentSlot.WEAPON)
    
    def get_enhancement_cost(self) -> int:
        """强化所需灵石"""
        if self.enhancement_level >= 20:
            return -1  # 满级
        base_cost = 50 * (self.quality.stars ** 2)
        return int(base_cost * (1.5 ** self.enhancement_level))
    
    def can_enhance(self, player) -> bool:
        """是否可以强化"""
        if self.enhancement_level >= 20:
            return False
        if player.level < self.level_required:
            return False
        return True
    
    def enhance(self, player) -> tuple:
        """
        强化装备
        返回 (success: bool, message: str)
        """
        if not self.can_enhance(player):
            if self.enhancement_level >= 20:
                return False, "强化等级已达上限"
            return False, f"需要{self.level_required}级"
        
        cost = self.get_enhancement_cost()
        if player.spirit_stones < cost:
            return False, f"需要{cost}灵石"
        
        # 强化成功概率
        success_rate = max(0.3, 1.0 - self.enhancement_level * 0.05)
        
        if random.random() < success_rate:
            player.spirit_stones -= cost
            self.enhancement_level += 1
            self.enhancement_bonus += 0.1  # 每次强化+10%
            return True, f"强化成功！{self.name} +{self.enhancement_level}"
        else:
            player.spirit_stones -= cost // 2
            return False, f"强化失败，损失{cost//2}灵石"
    
    def info(self) -> str:
        """装备信息"""
        stats = self.total_stats
        stats_dict = stats.to_dict()
        stats_str = " | ".join([f"{k}:{v}" for k, v in stats_dict.items()])
        
        element_str = f" [{self.element}]" if self.element else ""
        enhance_str = f" +{self.enhancement_level}" if self.enhancement_level > 0 else ""
        
        return f"""
【{self.name}{enhance_str}】{element_str}
品质: {self.quality.name} | 类型: {self.type.value} | 等级: {self.level_required}
{stats_str}
{self.description}
"""


# ============ 装备数据库 ============

def _create_weapon(template: tuple) -> Equipment:
    """创建武器
    template: (name, quality, attack, element, level_req, description)
    """
    name, quality, attack, element, level_req, description = template
    return Equipment(
        id=f"weapon_{name}",
        name=name,
        type=EquipmentType.WEAPON,
        quality=quality,
        level_required=level_req,
        base_stats=EquipmentStats(attack=attack),
        element=element,
        description=description or f"一把{quality.quality_name}级别的{name}"
    )


def _create_armor(template: tuple) -> Equipment:
    """创建防具
    template: (name, quality, defense, hp, level_req, description)
    """
    name, quality, defense, hp, level_req, description = template
    return Equipment(
        id=f"armor_{name}",
        name=name,
        type=EquipmentType.ARMOR,
        quality=quality,
        level_required=level_req,
        base_stats=EquipmentStats(defense=defense, hp=hp),
        description=description or f"一件{quality.quality_name}级别的{name}"
    )


# 武器模板
WEAPON_TEMPLATES = {
    # 凡品武器
    "iron_sword": ("铁剑", EquipmentQuality.MORTAL, 10, "金", 1, "普通的铁制长剑"),
    "wooden_staff": ("木杖", EquipmentQuality.MORTAL, 8, "木", 1, "简单的木制法杖"),
    "stone_axe": ("石斧", EquipmentQuality.MORTAL, 12, "土", 1, "粗重的石制斧头"),
    
    # 灵品武器
    "spirit_sword": ("灵剑", EquipmentQuality.SPIRIT, 25, "金", 5, "蕴含灵气的长剑"),
    "flame_staff": ("烈焰杖", EquipmentQuality.SPIRIT, 22, "火", 5, "附有火焰的魔法杖"),
    "frost_blade": ("寒冰刃", EquipmentQuality.SPIRIT, 23, "冰", 5, "冰冷锋利的刀刃"),
    "thunder_hammer": ("雷锤", EquipmentQuality.SPIRIT, 28, "雷", 8, "蕴含天雷之力的锤子"),
    
    # 神品武器
    "divine_sword": ("神剑", EquipmentQuality.DIVINE, 50, "金", 15, "神器级别的长剑"),
    "dragon_staff": ("龙杖", EquipmentQuality.DIVINE, 45, "火", 15, "传说中龙所使用的法杖"),
    "phoenix_bow": ("凤弓", EquipmentQuality.DIVINE, 48, "火", 15, "凤凰羽毛制成的弓"),
    "demon_blade": ("魔刀", EquipmentQuality.DIVINE, 55, "暗", 18, "蕴含魔力的邪刃"),
    
    # 天品武器
    "celestial_sword": ("天剑", EquipmentQuality.CELESTIAL, 100, "金", 25, "天界神兵"),
    "void_staff": ("虚空杖", EquipmentQuality.CELESTIAL, 95, "暗", 25, "能够扭曲空间的法杖"),
    "celestial_robe": ("天衣", EquipmentQuality.CELESTIAL, 0, "光", 25, "天界的仙衣"),
    
    # 仙品武器
    "immortal_sword": ("仙剑", EquipmentQuality.IMMORTAL, 200, "金", 40, "仙人使用的神剑"),
    "world_tree_staff": ("世界树之杖", EquipmentQuality.IMMORTAL, 180, "木", 40, "连接各界的神杖"),
}


# 防具模板
ARMOR_TEMPLATES = {
    # 凡品防具
    "leather_armor": ("皮甲", EquipmentQuality.MORTAL, 5, 20, 1, "简单的皮革护甲"),
    "cloth_robe": ("布袍", EquipmentQuality.MORTAL, 3, 30, 1, "基础的修炼者长袍"),
    
    # 灵品防具
    "spirit_armor": ("灵甲", EquipmentQuality.SPIRIT, 15, 50, 5, "蕴含灵气的护甲"),
    "flame_robe": ("火纹袍", EquipmentQuality.SPIRIT, 12, 60, 5, "刻有火焰纹路的法袍"),
    "frost_armor": ("冰晶甲", EquipmentQuality.SPIRIT, 14, 55, 5, "寒冰晶石打造的铠甲"),
    
    # 神品防具
    "divine_armor": ("神甲", EquipmentQuality.DIVINE, 30, 120, 15, "神器级别的铠甲"),
    "dragon_scale": ("龙鳞甲", EquipmentQuality.DIVINE, 35, 150, 18, "真龙鳞片制成的铠甲"),
    
    # 天品防具
    "celestial_robe": ("天袍", EquipmentQuality.CELESTIAL, 50, 200, 25, "天界的仙衣"),
    "thunder_armor": ("雷甲", EquipmentQuality.CELESTIAL, 55, 220, 28, "雷霆所化的铠甲"),
    
    # 仙品防具
    "immortal_robe": ("仙衣", EquipmentQuality.IMMORTAL, 100, 500, 40, "仙人所穿的仙衣"),
}


# 其他装备模板
ACCESSORY_TEMPLATES = {
    # 戒指
    "spirit_ring": ("灵戒", EquipmentQuality.SPIRIT, 10, 20, 3, "增加修炼速度"),
    "thunder_ring": ("雷戒", EquipmentQuality.DIVINE, 25, 40, 10, "雷属性戒指"),
    "celestial_ring": ("天戒", EquipmentQuality.CELESTIAL, 50, 80, 20, "天界仙戒"),
    
    # 项链
    "spirit_amulet": ("灵佩", EquipmentQuality.SPIRIT, 15, 30, 5, "增加灵气"),
    "health_amulet": ("血玉", EquipmentQuality.DIVINE, 0, 100, 12, "增加生命值"),
    "celestial_amulet": ("天珠", EquipmentQuality.CELESTIAL, 30, 100, 25, "天界宝物"),
    
    # 头盔
    "iron_helmet": ("铁帽", EquipmentQuality.MORTAL, 3, 10, 1, "简单头盔"),
    "spirit_helmet": ("灵帽", EquipmentQuality.SPIRIT, 8, 25, 5, "灵气头盔"),
    
    # 靴子
    "leather_boots": ("皮靴", EquipmentQuality.MORTAL, 0, 5, 1, "移动速度+1"),
    "wind_boots": ("风靴", EquipmentQuality.SPIRIT, 5, 20, 5, "增加速度"),
    "thunder_boots": ("雷靴", EquipmentQuality.DIVINE, 10, 40, 12, "雷属性速度"),
}


def generate_random_equipment(realm_level: int = 1) -> Equipment:
    """随机生成装备"""
    # 根据境界决定品质概率
    quality_roll = random.random()
    if realm_level >= 40:
        qualities = [EquipmentQuality.IMMORTAL, EquipmentQuality.CELESTIAL, EquipmentQuality.DIVINE]
        weights = [0.05, 0.20, 0.75]
    elif realm_level >= 25:
        qualities = [EquipmentQuality.CELESTIAL, EquipmentQuality.DIVINE, EquipmentQuality.SPIRIT]
        weights = [0.10, 0.40, 0.50]
    elif realm_level >= 15:
        qualities = [EquipmentQuality.DIVINE, EquipmentQuality.SPIRIT, EquipmentQuality.MORTAL]
        weights = [0.15, 0.55, 0.30]
    elif realm_level >= 5:
        qualities = [EquipmentQuality.SPIRIT, EquipmentQuality.MORTAL]
        weights = [0.40, 0.60]
    else:
        qualities = [EquipmentQuality.MORTAL]
        weights = [1.0]
    
    quality = random.choices(qualities, weights=weights)[0]
    
    # 随机选择装备类型（按概率）
    type_choices = [
        (EquipmentType.WEAPON, WEAPON_TEMPLATES, 0.35),
        (EquipmentType.ARMOR, ARMOR_TEMPLATES, 0.30),
        (EquipmentType.RING, {k: v for k, v in ACCESSORY_TEMPLATES.items() if "ring" in k}, 0.15),
        (EquipmentType.AMULET, {k: v for k, v in ACCESSORY_TEMPLATES.items() if "amulet" in k}, 0.10),
        (EquipmentType.HELMET, {k: v for k, v in ACCESSORY_TEMPLATES.items() if "helmet" in k}, 0.05),
        (EquipmentType.BOOTS, {k: v for k, v in ACCESSORY_TEMPLATES.items() if "boots" in k}, 0.05),
    ]
    
    # 归一化权重
    total_weight = sum(x[2] for x in type_choices)
    type_choices = [(t, templates, w/total_weight) for t, templates, w in type_choices]
    
    equip_type, templates, _ = random.choices(type_choices, weights=[x[2] for x in type_choices])[0]
    
    if not templates:
        # 备用：使用所有配件模板
        templates = ACCESSORY_TEMPLATES
    
    # 筛选符合条件的模板（根据品质）
    valid_templates = {k: v for k, v in templates.items() if v[1].stars <= quality.stars}
    
    if not valid_templates:
        valid_templates = templates
    
    template_key = random.choice(list(valid_templates.keys()))
    template = valid_templates[template_key]
    
    # 创建装备
    if equip_type == EquipmentType.WEAPON:
        equip = _create_weapon(template)
    elif equip_type == EquipmentType.ARMOR:
        equip = _create_armor(template)
    else:
        # 饰品
        name, qual, atk, hp, lvl, desc = template
        equip = Equipment(
            id=f"accessory_{template_key}",
            name=name,
            type=equip_type,
            quality=qual,
            level_required=lvl,
            base_stats=EquipmentStats(attack=atk, hp=hp),
            description=desc
        )
    
    # 添加稀有属性（概率生成）
    if random.random() < 0.3 * quality.stars:
        rare = EquipmentStats()
        rare_stat = random.choice(["attack", "defense", "hp", "crit", "speed"])
        if rare_stat == "attack":
            rare.attack = int(equip.base_stats.attack * 0.2)
        elif rare_stat == "defense":
            rare.defense = int(equip.base_stats.defense * 0.2)
        elif rare_stat == "hp":
            rare.hp = int(equip.base_stats.hp * 0.3)
        elif rare_stat == "crit":
            rare.crit = 0.05
        elif rare_stat == "speed":
            rare.speed = 0.1
        equip.rare_stats = rare
    
    return equip


# ============ 装备系统 ============

class EquipmentSystem:
    """装备系统"""
    
    @staticmethod
    def can_equip(player, equipment: Equipment) -> tuple:
        """
        检查是否可以装备
        返回 (can_equip: bool, reason: str)
        """
        if player.level < equipment.level_required:
            return False, f"需要{equipment.level_required}级"
        return True, ""
    
    @staticmethod
    def equip(player, equipment: Equipment) -> tuple:
        """
        穿戴装备
        返回 (success: bool, message: str)
        """
        can_equip, reason = EquipmentSystem.can_equip(player, equipment)
        if not can_equip:
            return False, reason
        
        # 获取装备槽位
        slot = equipment.slot
        
        # 处理戒指特殊情况
        if equipment.type == EquipmentType.RING:
            if not getattr(player, f"ring1", None):
                slot = EquipmentSlot.RING1
            elif not getattr(player, f"ring2", None):
                slot = EquipmentSlot.RING2
            else:
                # 已有两个戒指，询问替换
                slot = EquipmentSlot.RING1
        
        # 记录旧装备（用于替换）
        old_equip = getattr(player, slot.value, None)
        
        # 装备新装备
        setattr(player, slot.value, equipment)
        
        # 更新玩家属性
        EquipmentSystem.apply_equipment_bonus(player)
        
        if old_equip:
            return True, f"替换装备成功！\n卸下: {old_equip.name}\n穿上: {equipment.name}"
        return True, f"装备成功: {equipment.name}"
    
    @staticmethod
    def unequip(player, slot: EquipmentSlot) -> tuple:
        """
        卸下装备
        返回 (success: bool, message: str)
        """
        equip = getattr(player, slot.value, None)
        if not equip:
            return False, "该槽位没有装备"
        
        setattr(player, slot.value, None)
        EquipmentSystem.apply_equipment_bonus(player)
        
        return True, f"卸下装备: {equip.name}"
    
    @staticmethod
    def apply_equipment_bonus(player):
        """应用装备属性加成"""
        # 基础属性（不含装备）
        base_attack = 10
        base_defense = 5
        base_max_hp = 100
        base_max_qi = 100
        
        # 遍历所有装备槽位累加属性
        equipment_bonus = EquipmentStats()
        
        for slot in EquipmentSlot:
            equip = getattr(player, slot.value, None)
            if equip:
                stats = equip.total_stats
                equipment_bonus.attack += stats.attack
                equipment_bonus.defense += stats.defense
                equipment_bonus.hp += stats.hp
                equipment_bonus.qi += stats.qi
                equipment_bonus.crit += stats.crit
                equipment_bonus.speed += stats.speed
                equipment_bonus.cultivation_speed += stats.cultivation_speed
        
        # 设置玩家属性
        player.attack = base_attack + equipment_bonus.attack
        player.defense = base_defense + equipment_bonus.defense
        player.max_hp = base_max_hp + equipment_bonus.hp
        player.max_qi = base_max_qi + equipment_bonus.qi
        player.crit = equipment_bonus.crit
        player.speed = 1.0 + equipment_bonus.speed
        player.cultivation_speed = 1.0 + equipment_bonus.cultivation_speed
        
        # 应用灵根和功法加成
        player.apply_element_bonuses()
        
        # 恢复生命和灵气到上限
        player.hp = min(player.hp, player.max_hp)
        player.qi = min(player.qi, player.max_qi)
    
    @staticmethod
    def get_equipment_list(player) -> List[Equipment]:
        """获取玩家所有装备"""
        equipment_list = []
        for slot in EquipmentSlot:
            equip = getattr(player, slot.value, None)
            if equip:
                equipment_list.append(equip)
        return equipment_list
    
    @staticmethod
    def get_equipment_by_slot(player, slot: EquipmentSlot) -> Optional[Equipment]:
        """获取指定槽位的装备"""
        return getattr(player, slot.value, None)
    
    @staticmethod
    def get_total_equipment_stats(player) -> EquipmentStats:
        """获取装备总属性"""
        total = EquipmentStats()
        for slot in EquipmentSlot:
            equip = getattr(player, slot.value, None)
            if equip:
                total = total.add(equip.total_stats)
        return total


# ============ 装备商店 ============

@dataclass
class ShopItem:
    """商店物品"""
    equipment: Equipment
    price: int
    stock: int = -1  # -1 表示无限


class EquipmentShop:
    """装备商店"""
    
    def __init__(self):
        self.items: List[ShopItem] = []
        self._init_shop()
    
    def _init_shop(self):
        """初始化商店"""
        # 根据品质和类型添加商品
        for template_key, template in WEAPON_TEMPLATES.items():
            equip = _create_weapon(template)
            price = self._calculate_price(equip)
            self.items.append(ShopItem(equipment=equip, price=price))
        
        for template_key, template in ARMOR_TEMPLATES.items():
            equip = _create_armor(template)
            price = self._calculate_price(equip)
            self.items.append(ShopItem(equipment=equip, price=price))
        
        for template_key, template in ACCESSORY_TEMPLATES.items():
            name, qual, atk, hp, lvl, desc = template
            equip = Equipment(
                id=f"accessory_{template_key}",
                name=name,
                type=EquipmentType.RING if "ring" in template_key else 
                     EquipmentType.AMULET if "amulet" in template_key else
                     EquipmentType.HELMET if "helmet" in template_key else EquipmentType.BOOTS,
                quality=qual,
                level_required=lvl,
                base_stats=EquipmentStats(attack=atk, hp=hp),
                description=desc
            )
            price = self._calculate_price(equip)
            self.items.append(ShopItem(equipment=equip, price=price))
    
    def _calculate_price(self, equip: Equipment) -> int:
        """计算装备价格"""
        base = 10
        stats = equip.base_stats
        base += stats.attack * 2
        base += stats.defense * 2
        base += stats.hp // 2
        base *= equip.quality.stars ** 1.5
        return int(base)
    
    def get_items_by_type(self, equip_type: EquipmentType) -> List[ShopItem]:
        """按类型获取商品"""
        return [item for item in self.items if item.equipment.type == equip_type]
    
    def get_items_by_quality(self, quality: EquipmentQuality) -> List[ShopItem]:
        """按品质获取商品"""
        return [item for item in self.items if item.equipment.quality == quality]
    
    def buy(self, player, item_index: int) -> tuple:
        """
        购买装备
        返回 (success: bool, message: str)
        """
        if item_index < 0 or item_index >= len(self.items):
            return False, "商品不存在"
        
        item = self.items[item_index]
        
        if item.stock == 0:
            return False, "该商品已售罄"
        
        if player.spirit_stones < item.price:
            return False, f"灵石不足，需要{item.price}灵石"
        
        player.spirit_stones -= item.price
        
        if item.stock > 0:
            item.stock -= 1
        
        # 直接装备或返回
        return True, f"购买成功！\n花费: {item.price}灵石\n获得: {item.equipment.name}"


# 全局商店实例
equipment_shop = EquipmentShop()
