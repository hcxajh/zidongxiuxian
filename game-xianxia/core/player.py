"""
修仙游戏核心框架 - 玩家模块
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import random


class Realm(Enum):
    """境界枚举"""
    MORTAL = "凡人"
    QI_REFINING = "炼气期"
    FOUNDATION = "筑基期"
    GOLDEN_CORE = "金丹期"
    NASENT_SOUL = "元婴期"
    TRANSFORMATION = "化神期"
    VOID = "合体期"
    DHARMA = "大乘期"
    IMMORTAL = "仙人"
    
    @property
    def level_cap(self) -> int:
        """每境界最大层数"""
        caps = {
            Realm.MORTAL: 0,
            Realm.QI_REFINING: 10,
            Realm.FOUNDATION: 10,
            Realm.GOLDEN_CORE: 10,
            Realm.NASENT_SOUL: 10,
            Realm.TRANSFORMATION: 10,
            Realm.VOID: 10,
            Realm.DHARMA: 10,
            Realm.IMMORTAL: 10,
        }
        return caps.get(self, 10)
    
    @property
    def breakthrough_cost(self) -> int:
        """突破所需灵石"""
        costs = {
            Realm.MORTAL: 0,
            Realm.QI_REFINING: 100,
            Realm.FOUNDATION: 500,
            Realm.GOLDEN_CORE: 2000,
            Realm.NASENT_SOUL: 10000,
            Realm.TRANSFORMATION: 50000,
            Realm.VOID: 200000,
            Realm.DHARMA: 1000000,
            Realm.IMMORTAL: 5000000,
        }
        return costs.get(self, 0)


# 境界压制配置
REALM_SUPPRESSION = {
    0: {"bonus": 1.0, "penalty": 1.0},   # 同阶
    1: {"bonus": 1.3, "penalty": 0.7},   # 高1阶
    2: {"bonus": 1.6, "penalty": 0.5},   # 高2阶
    3: {"bonus": 2.0, "penalty": 0.3},   # 高3阶及以上
}


# 保留旧接口兼容
Element = None  # 将在运行时导入


@dataclass
class Player:
    """玩家角色"""
    name: str
    level: int = 1  # 当前境界层数
    realm: Realm = Realm.MORTAL
    qi: float = 0.0  # 当前灵气
    max_qi: float = 100.0  # 最大灵气
    hp: float = 100.0  # 生命值
    max_hp: float = 100.0  # 最大生命值
    spirit_stones: int = 100  # 灵石
    
    # 灵根 (使用新的Element类)
    elements: List = field(default_factory=list)
    
    # 功法 {skill_id: PlayerSkill}
    skills: Dict = field(default_factory=dict)
    
    # 装备槽位 - 存储 Equipment 对象
    weapon: Optional['Equipment'] = None
    armor: Optional['Equipment'] = None
    helmet: Optional['Equipment'] = None
    boots: Optional['Equipment'] = None
    ring1: Optional['Equipment'] = None
    ring2: Optional['Equipment'] = None
    amulet: Optional['Equipment'] = None
    belt: Optional['Equipment'] = None
    
    # 背包
    inventory: List = field(default_factory=list)
    
    # 属性
    attack: int = 10
    defense: int = 5
    cultivation_speed: float = 1.0
    crit: float = 0.0  # 暴击率
    speed: float = 1.0  # 速度
    
    # 战斗状态
    cooldowns: Dict[str, int] = field(default_factory=dict)
    
    # 修为系统
    cultivation: float = 0.0  # 当前修为
    total_cultivation: float = 0.0  # 累计修为
    
    def __post_init__(self):
        """初始化后处理"""
        # 延迟导入避免循环依赖
        global Element
        if Element is None:
            try:
                from core.element import Element
            except ImportError:
                pass
    
    @property
    def elements_list(self) -> List:
        """兼容属性"""
        return self.elements
    
    def gain_qi(self, amount: float) -> float:
        """获得灵气"""
        overflow = 0.0
        self.qi += amount
        if self.qi > self.max_qi:
            overflow = self.qi - self.max_qi
            self.qi = self.max_qi
        return overflow
    
    def consume_qi(self, amount: float) -> bool:
        """消耗灵气"""
        if self.qi >= amount:
            self.qi -= amount
            return True
        return False
    
    def take_damage(self, damage: int) -> int:
        """受到伤害，返回实际受到的伤害"""
        actual_damage = max(1, damage - self.defense)
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage
    
    def heal(self, amount: float) -> float:
        """恢复生命"""
        actual_heal = min(amount, self.max_hp - self.hp)
        self.hp += actual_heal
        return actual_heal
    
    def can_breakthrough(self) -> bool:
        """检查是否可以突破"""
        return self.qi >= self.max_qi and self.level >= self.realm.level_cap
    
    def breakthrough(self) -> bool:
        """突破境界"""
        if not self.can_breakthrough():
            return False
        
        cost = self.realm.breakthrough_cost
        if self.spirit_stones < cost:
            return False
        
        # 境界提升
        realm_index = list(Realm).index(self.realm)
        if realm_index < len(Realm) - 1:
            self.spirit_stones -= cost
            self.realm = list(Realm)[realm_index + 1]
            self.level = 1
            self.max_qi *= 2.0
            self.qi = 0
            self.max_hp *= 1.5
            self.hp = self.max_hp
            self.attack += 5
            self.defense += 3
            return True
        return False
    
    def tick_cooldowns(self):
        """减少技能冷却"""
        for skill_id in list(self.cooldowns.keys()):
            self.cooldowns[skill_id] -= 1
            if self.cooldowns[skill_id] <= 0:
                del self.cooldowns[skill_id]
    
    def apply_element_bonuses(self):
        """应用灵根加成"""
        if not self.elements:
            return
        
        try:
            from core.element import ElementSystem
            synergy = ElementSystem.calculate_element_synergy(self.elements)
            
            self.attack = int(self.attack * synergy.get("attack", 1.0))
            self.defense = int(self.defense * synergy.get("defense", 1.0))
            self.cultivation_speed *= synergy.get("cultivation", 1.0)
            self.crit += synergy.get("crit", 0.0)
            self.speed *= synergy.get("speed", 1.0)
            self.max_hp *= synergy.get("hp", 1.0)
        except ImportError:
            pass
    
    def gain_cultivation(self, amount: float) -> float:
        """获得修为"""
        self.cultivation += amount
        self.total_cultivation += amount
        return amount
    
    def get_level_up_requirement(self) -> float:
        """获取升级到下一层需要的修为"""
        base = 100.0
        return base * (self.level ** 1.5)
    
    def can_level_up(self) -> bool:
        """检查是否可以升级层数"""
        if self.level >= self.realm.level_cap:
            return False
        return self.cultivation >= self.get_level_up_requirement()
    
    def level_up(self) -> bool:
        """
        提升境界层数
        返回是否成功
        """
        if not self.can_level_up():
            return False
        
        required = self.get_level_up_requirement()
        self.cultivation -= required
        
        # 层数提升
        self.level += 1
        
        # 属性提升
        realm_index = list(Realm).index(self.realm)
        level_bonus = 1 + realm_index * 0.5
        
        self.max_qi *= 1.1
        self.attack += int(2 * level_bonus)
        self.defense += int(1 * level_bonus)
        
        return True
    
    @staticmethod
    def get_realm_suppression(attacker_realm: Realm, defender_realm: Realm) -> dict:
        """
        获取境界压制效果
        返回 {"bonus": 攻击加成, "penalty": 受伤减免}
        """
        attacker_idx = list(Realm).index(attacker_realm)
        defender_idx = list(Realm).index(defender_realm)
        
        diff = defender_idx - attacker_idx
        
        if diff <= 0:
            return REALM_SUPPRESSION[min(-diff, 3)]
        else:
            return REALM_SUPPRESSION[min(diff, 3)]
    
    def status(self) -> str:
        """获取状态字符串"""
        elements_str = ""
        if self.elements:
            try:
                from core.element import Element
                elements_str = ", ".join([e.name if hasattr(e, 'name') else str(e) for e in self.elements])
            except:
                elements_str = str(self.elements)
        
        skills_str = ""
        if self.skills:
            try:
                from core.skill import SKILLS_DATABASE
                skill_names = []
                for sid, ps in self.skills.items():
                    skill = SKILLS_DATABASE.get(sid)
                    if skill:
                        skill_names.append(f"{skill.name}L{ps.level}")
                skills_str = ", ".join(skill_names)
            except:
                skills_str = str(list(self.skills.keys()))
        
        return f"""
╔══════════════════════════════╗
║ 【{self.name}】                 ║
╠══════════════════════════════╣
║ 境界: {self.realm.value} 第{self.level}/{self.realm.level_cap}层     ║
║ 灵气: {self.qi:.1f}/{self.max_qi:.1f} ({self.qi/self.max_qi*100:.0f}%)      ║
║ 生命: {self.hp:.1f}/{self.max_hp:.1f}          ║
║ 灵石: {self.spirit_stones}                 ║
╠══════════════════════════════╣
║ 攻击: {self.attack} | 防御: {self.defense}    ║
║ 暴击: {self.crit*100:.0f}% | 速度: {self.speed:.1f}x   ║
║ 修炼: {self.cultivation_speed:.2f}x              ║
╠══════════════════════════════╣
║ 修为: {self.cultivation:.0f}/{self.get_level_up_requirement():.0f}          ║
║ 灵根: {elements_str or '无'}     ║
║ 功法: {skills_str or '无'}       ║
║ 装备: {self.weapon or '无'} / {self.armor or '无'} ║
╚══════════════════════════════╝
"""


def create_player(name: str, elements: List = None) -> Player:
    """创建玩家"""
    player = Player(name=name)
    
    if elements:
        player.elements = elements
        player.apply_element_bonuses()
    else:
        # 随机生成灵根
        try:
            from core.element import ElementSystem, generate_element_with_grade
            # 尝试生成2-3个灵根
            import random
            num_elements = random.randint(1, 3)
            player.elements = ElementSystem.generate_player_elements(
                num_elements, 
                grade_range=(5, 9)
            )
            player.apply_element_bonuses()
        except ImportError:
            pass
    
    return player
