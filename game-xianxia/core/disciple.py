"""
修仙游戏 - 弟子系统
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import random


class DiscipleState(Enum):
    """弟子状态"""
    ACTIVE = "修炼中"
    COMBAT = "战斗中"
    IDLE = "空闲"
    DISCIPLINE = "受罚中"


class DiscipleTalent(Enum):
    """弟子天赋"""
    SPIRITUAL = "悟性极高"      # 修炼速度快
    COMBAT = "战斗天才"          # 战斗力强
    DEFENSIVE = "铜皮铁骨"        # 防御高
    AGILE = "身法灵动"            # 速度快
    RICH = "福缘深厚"            # 掉落加成
    LONG_LIVED = "寿元悠长"       # 境界上限高


@dataclass
class DiscipleTribe:
    """弟子种族/体质"""
    HUMAN = "人族"
    DEMON = "妖族"
    SPIRIT = "灵族"
    UNDEAD = "鬼族"


@dataclass
class Disciple:
    """弟子"""
    id: str
    name: str
    level: int = 1  # 境界层数
    realm: str = "炼气期"
    
    # 灵根属性 (元素类型列表)
    elements: List[str] = field(default_factory=list)
    
    # 种族
    tribe: str = "人族"
    
    # 天赋 (可多个)
    talents: List[str] = field(default_factory=list)
    
    # 状态
    state: DiscipleState = DiscipleState.IDLE
    
    # 修为
    cultivation: float = 0.0
    
    # 战斗属性
    attack: int = 5
    defense: int = 3
    hp: int = 50
    max_hp: int = 50
    qi: int = 50
    max_qi: int = 50
    
    # 特殊属性
    crit: float = 0.05  # 暴击率
    speed: float = 1.0
    luck: float = 1.0   # 运气
    
    # 忠诚度
    loyalty: int = 100
    
    # 培养时间 (小时)
    training_hours: float = 0.0
    
    # 战功
    merits: int = 0
    
    # 装备
    weapon: Optional[str] = None
    armor: Optional[str] = None
    
    # 心情
    mood: int = 100
    
    def get_talent_bonus(self, bonus_type: str) -> float:
        """获取天赋加成"""
        multiplier = 1.0
        for talent in self.talents:
            if bonus_type == "cultivation" and talent == "悟性极高":
                multiplier += 0.5
            elif bonus_type == "attack" and talent == "战斗天才":
                multiplier += 0.5
            elif bonus_type == "defense" and talent == "铜皮铁骨":
                multiplier += 0.5
            elif bonus_type == "speed" and talent == "身法灵动":
                multiplier += 0.3
            elif bonus_type == "luck" and talent == "福缘深厚":
                multiplier += 0.5
        return multiplier
    
    def can_level_up(self, requirement: float) -> bool:
        """是否可以升级"""
        return self.cultivation >= requirement
    
    def level_up(self) -> bool:
        """升级"""
        realm_levels = {
            "炼气期": 10,
            "筑基期": 10,
            "金丹期": 10,
            "元婴期": 10,
            "化神期": 10,
        }
        max_level = realm_levels.get(self.realm, 10)
        
        if self.level >= max_level:
            return False
        
        self.level += 1
        self.max_hp += 10
        self.hp = self.max_hp
        self.max_qi += 10
        self.qi = self.max_qi
        self.attack += 2
        self.defense += 1
        return True
    
    def train(self, hours: float) -> Dict:
        """修炼"""
        base_cultivation = 10 * hours
        talent_bonus = self.get_talent_bonus("cultivation")
        cultivation_gain = base_cultivation * talent_bonus
        
        self.cultivation += cultivation_gain
        self.training_hours += hours
        
        # 随机增加一些属性
        if random.random() < 0.1 * hours:
            self.attack += 1
        if random.random() < 0.05 * hours:
            self.defense += 1
            
        return {
            "cultivation_gain": cultivation_gain,
            "new_cultivation": self.cultivation
        }
    
    def take_damage(self, damage: int) -> int:
        """受到伤害"""
        actual = max(1, damage - self.defense)
        self.hp = max(0, self.hp - actual)
        return actual
    
    def heal(self, amount: int) -> int:
        """恢复"""
        actual = min(amount, self.max_hp - self.hp)
        self.hp += actual
        return actual
    
    def update_loyalty(self, change: int):
        """更新忠诚度"""
        self.loyalty = max(0, min(100, self.loyalty + change))
        # 心情随忠诚度变化
        self.mood = max(0, min(100, self.loyalty))
    
    def status(self) -> str:
        """状态显示"""
        talents_str = ", ".join(self.talents) if self.talents else "无"
        elements_str = ", ".join(self.elements) if self.elements else "无"
        
        return f"""
【{self.name}】
  境界: {self.realm} 第{self.level}层
  种族: {self.tribe} | 天赋: {talents_str}
  灵根: {elements_str}
  忠诚: {self.loyalty}% | 心情: {self.mood}%
  修为: {self.cultivation:.0f}
  HP: {self.hp}/{self.max_hp} | Qi: {self.qi}/{self.max_qi}
  攻击: {self.attack} | 防御: {self.defense}
  暴击: {self.crit*100:.0f}% | 速度: {self.speed:.1f}x
  状态: {self.state.value}
  战功: {self.merits}
"""


class DiscipleSystem:
    """弟子管理系统"""
    
    # 弟子名字库
    FIRST_NAMES = ["云", "风", "雷", "雨", "雪", "霜", "星", "月", "日", "天",
                   "青", "蓝", "紫", "红", "白", "黑", "玉", "明", "清", "玄"]
    LAST_NAMES = ["鹤", "松", "竹", "梅", "兰", "菊", "雁", "鹏", "龙", "虎",
                  "羽", "尘", "轩", "岚", "峰", "岩", "泉", "溪", "海", "云"]
    
    # 可用天赋池
    TALENT_POOL = [
        "悟性极高", "战斗天才", "铜皮铁骨", "身法灵动", "福缘深厚", "寿元悠长"
    ]
    
    @staticmethod
    def generate_disciple(realm_level: int = 1) -> Disciple:
        """生成随机弟子"""
        # 生成ID
        disciple_id = f"disciple_{random.randint(10000, 99999)}"
        
        # 生成名字
        first = random.choice(DiscipleSystem.FIRST_NAMES)
        last = random.choice(DiscipleSystem.LAST_NAMES)
        name = f"{first}{last}"
        
        # 随机种族
        tribes = ["人族", "妖族", "灵族"]
        tribe = random.choice(tribes)
        
        # 随机天赋 (1-2个)
        num_talents = random.randint(1, 2)
        talents = random.sample(DiscipleSystem.TALENT_POOL, num_talents)
        
        # 根据境界设置基础属性
        base_hp = 50 + realm_level * 10
        base_attack = 5 + realm_level * 2
        base_defense = 3 + realm_level
        
        # 随机灵根
        elements_pool = ["金", "木", "水", "火", "土", "雷", "冰", "风"]
        num_elements = random.randint(1, 2)
        elements = random.sample(elements_pool, num_elements)
        
        disciple = Disciple(
            id=disciple_id,
            name=name,
            level=realm_level,
            realm="炼气期",
            elements=elements,
            tribe=tribe,
            talents=talents,
            hp=base_hp,
            max_hp=base_hp,
            qi=base_hp,
            max_qi=base_hp,
            attack=base_attack,
            defense=base_defense,
        )
        
        return disciple
    
    @staticmethod
    def recruit_disciple(player_disciples: List[Disciple], realm: str) -> Disciple:
        """招收弟子"""
        realm_map = {
            "凡人": 1, "炼气期": 1, "筑基期": 2, "金丹期": 3, 
            "元婴期": 4, "化神期": 5, "合体期": 6, "大乘期": 7
        }
        realm_index = realm_map.get(realm, 1)
        return DiscipleSystem.generate_disciple(realm_index)
    
    @staticmethod
    def train_disciple(disciple: Disciple, hours: float) -> Dict:
        """指导弟子修炼"""
        result = disciple.train(hours)
        
        # 检查升级
        realm_levels = {
            "炼气期": 100,
            "筑基期": 500,
            "金丹期": 2000,
            "元婴期": 10000,
            "化神期": 50000,
        }
        
        while disciple.can_level_up(realm_levels.get(disciple.realm, 100)):
            if disciple.level_up():
                # 忠诚度提升
                disciple.update_loyalty(2)
                result["leveled_up"] = True
                result["new_level"] = disciple.level
            else:
                break
        
        return result
    
    @staticmethod
    def send_to_combat(disciple: Disciple, enemy_level: int) -> Dict:
        """派遣弟子战斗"""
        disciple.state = DiscipleState.COMBAT
        
        enemy_hp = 30 + enemy_level * 15
        enemy_attack = 3 + enemy_level * 2
        
        combat_log = []
        
        while disciple.hp > 0 and enemy_hp > 0:
            # 弟子攻击
            damage = disciple.attack
            if random.random() < disciple.crit:
                damage = int(damage * 1.5)
                combat_log.append(f"暴击! 弟子对敌人造成 {damage} 点伤害")
            else:
                combat_log.append(f"弟子对敌人造成 {damage} 点伤害")
            
            enemy_hp -= damage
            
            if enemy_hp <= 0:
                break
            
            # 敌人攻击
            actual_damage = disciple.take_damage(enemy_attack)
            combat_log.append(f"敌人对弟子造成 {actual_damage} 点伤害")
        
        disciple.state = DiscipleState.IDLE
        
        if disciple.hp > 0:
            merits = enemy_level * 10 + 20
            disciple.merits += merits
            disciple.update_loyalty(5)
            return {
                "win": True,
                "merits": merits,
                "log": combat_log
            }
        else:
            disciple.update_loyalty(-10)
            return {
                "win": False,
                "merits": 0,
                "log": combat_log
            }
    
    @staticmethod
    def dismiss_disciple(disciple: Disciple, reason: str = "主动驱逐") -> str:
        """驱逐弟子"""
        return f"弟子 {disciple.name} 已{reason}，永久离开宗门"
    
    @staticmethod
    def get_disciple_summary(disciples: List[Disciple]) -> str:
        """获取弟子概览"""
        if not disciples:
            return "暂无弟子"
        
        lines = ["【宗门弟子】"]
        for i, d in enumerate(disciples, 1):
            lines.append(f"{i}. {d.name} - {d.realm}第{d.level}层 (忠诚:{d.loyalty}%)")
        
        return "\n".join(lines)
