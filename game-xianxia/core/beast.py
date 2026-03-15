"""
修仙游戏 - 灵兽伙伴系统
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import random


class BeastType(Enum):
    """灵兽类型"""
    WOLF = "狼族"
    FOX = "狐族"
    TIGER = "虎族"
    DRAGON = "龙族"
    PHOENIX = "凤凰族"
    TURTLE = "龟族"
    BIRD = "禽族"
    SNAKE = "蛇族"
    SPIRIT = "精灵族"
    INSECT = "虫族"


class BeastQuality(Enum):
    """灵兽品质"""
    COMMON = 1      # 普通
    RARE = 2        # 稀有
    ELITE = 3       # 精英
    LEGENDARY = 4   # 传说
    MYTHICAL = 5    # 神话


class BeastState(Enum):
    """灵兽状态"""
    IDLE = "空闲"
    BATTLE = "战斗中"
    RESTING = "休息中"
    TRAINING = "修炼中"


@dataclass
class BeastSkill:
    """灵兽技能"""
    name: str
    description: str
    damage_bonus: float = 0.0   # 伤害加成
    defense_bonus: int = 0      # 防御加成
    heal_bonus: int = 0         # 治疗加成
    crit_bonus: float = 0.0     # 暴击加成
    speed_bonus: float = 0.0    # 速度加成


@dataclass
class Beast:
    """灵兽伙伴"""
    id: str
    name: str
    type: BeastType
    
    # 品质
    quality: BeastQuality = BeastQuality.COMMON
    
    # 境界 (与玩家境界对应)
    level: int = 1
    realm: str = "炼气期"
    
    # 亲密度
    intimacy: int = 50
    
    # 状态
    state: BeastState = BeastState.IDLE
    
    # 战斗属性
    attack: int = 8
    defense: int = 4
    hp: int = 60
    max_hp: int = 60
    qi: int = 40
    max_qi: int = 40
    
    # 特殊属性
    crit: float = 0.08
    speed: float = 1.2
    
    # 忠诚度
    loyalty: int = 80
    
    # 经验
    experience: float = 0.0
    total_experience: float = 0.0
    
    # 技能
    skills: List[BeastSkill] = field(default_factory=list)
    
    # 进化阶段
    evolution_stage: int = 1
    
    # 心情
    mood: int = 80
    
    # 饱食度
    fullness: int = 100
    
    # 装备
    equipment: Dict[str, str] = field(default_factory=dict)
    
    def get_quality_name(self) -> str:
        """获取品质名称"""
        names = {
            BeastQuality.COMMON: "普通",
            BeastQuality.RARE: "稀有",
            BeastQuality.ELITE: "精英",
            BeastQuality.LEGENDARY: "传说",
            BeastQuality.MYTHICAL: "神话",
        }
        return names.get(self.quality, "普通")
    
    def get_quality_color(self) -> str:
        """获取品质颜色"""
        colors = {
            BeastQuality.COMMON: "白色",
            BeastQuality.RARE: "蓝色",
            BeastQuality.ELITE: "紫色",
            BeastQuality.LEGENDARY: "橙色",
            BeastQuality.MYTHICAL: "红色",
        }
        return colors.get(self.quality, "白色")
    
    def can_evolution(self) -> bool:
        """是否可以进化"""
        evolution_requirements = {
            1: 100,   # 1阶升2阶需要100经验
            2: 500,
            3: 2000,
            4: 10000,
        }
        required = evolution_requirements.get(self.evolution_stage, 99999)
        return self.total_experience >= required
    
    def evolution(self) -> bool:
        """进化"""
        if not self.can_evolution():
            return False
        
        self.evolution_stage += 1
        
        # 属性大幅提升
        self.max_hp = int(self.max_hp * 1.5)
        self.hp = self.max_hp
        self.max_qi = int(self.max_qi * 1.3)
        self.qi = self.max_qi
        self.attack = int(self.attack * 1.4)
        self.defense = int(self.defense * 1.3)
        self.crit += 0.02
        self.speed *= 1.1
        
        return True
    
    def gain_experience(self, exp: float) -> Dict:
        """获得经验"""
        # 亲密度加成
        intimacy_bonus = 1.0 + (self.intimacy / 200.0)
        actual_exp = exp * intimacy_bonus
        
        self.experience += actual_exp
        self.total_experience += actual_exp
        
        leveled_up = False
        new_level = self.level
        
        # 检查升级
        exp_requirement = self.level * 50
        while self.experience >= exp_requirement:
            self.level += 1
            self.experience -= exp_requirement
            leveled_up = True
            new_level = self.level
            
            # 升级属性提升
            self.max_hp += 8
            self.hp = self.max_hp
            self.max_qi += 5
            self.qi = self.max_qi
            self.attack += 2
            self.defense += 1
            
            exp_requirement = self.level * 50
        
        return {
            "exp_gained": actual_exp,
            "leveled_up": leveled_up,
            "new_level": new_level,
            "can_evolution": self.can_evolution()
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
    
    def update_intimacy(self, change: int):
        """更新亲密度"""
        self.intimacy = max(0, min(100, self.intimacy + change))
        self.mood = max(0, min(100, self.intimacy))
    
    def feed(self, food_quality: int = 1) -> Dict:
        """喂食"""
        # 饱食度增加
        fullness_gain = min(30, food_quality * 10)
        self.fullness = min(100, self.fullness + fullness_gain)
        
        # 亲密度增加
        intimacy_gain = food_quality
        self.update_intimacy(intimacy_gain)
        
        return {
            "fullness": self.fullness,
            "intimacy": self.intimacy,
            "intimacy_gain": intimacy_gain
        }
    
    def train(self, hours: float) -> Dict:
        """训练"""
        if self.state == BeastState.BATTLE:
            return {"error": "战斗中无法训练"}
        
        self.state = BeastState.TRAINING
        
        # 基础经验获取
        base_exp = 5 * hours * self.quality.value
        result = self.gain_experience(base_exp)
        
        # 心情变化
        if random.random() < 0.2 * hours:
            self.mood = min(100, self.mood + 5)
        
        self.state = BeastState.IDLE
        result["message"] = f"训练 {hours} 小时，获得 {result['exp_gained']:.1f} 经验"
        
        return result
    
    def status(self) -> str:
        """状态显示"""
        skills_str = ", ".join([s.name for s in self.skills]) if self.skills else "无"
        
        return f"""
【{self.name}】({self.get_quality_name()}{self.type.value})
  境界: {self.realm}第{self.level}层 | 进化阶段: {self.evolution_stage}
  亲密度: {self.intimacy}% | 忠诚度: {self.loyalty}%
  心情: {self.mood}% | 饱食度: {self.fullness}%
  HP: {self.hp}/{self.max_hp} | Qi: {self.qi}/{self.max_qi}
  攻击: {self.attack} | 防御: {self.defense}
  暴击: {self.crit*100:.0f}% | 速度: {self.speed:.1f}x
  经验: {self.experience:.0f}/{self.level*50} | 技能: {skills_str}
  状态: {self.state.value}
"""


class BeastSystem:
    """灵兽管理系统"""
    
    # 灵兽名字库
    BEAST_NAMES = {
        BeastType.WOLF: ["银牙", "赤焰", "青风", "雪狼", "雷爪", "幽影"],
        BeastType.FOX: ["青丘", "九尾", "雪狐", "火狐", "银狐", "媚儿"],
        BeastType.TIGER: ["白虎", "赤焰", "烈风", "啸天", "金睛", "奔雷"],
        BeastType.DRAGON: ["青龙", "赤龙", "白龙", "黑龙", "金龙", "应龙"],
        BeastType.PHOENIX: ["朱雀", "青鸾", "火凤", "冰凤", "金凤", "彩凤"],
        BeastType.TURTLE: ["玄武", "长寿", "铁背", "灵龟", "龙龟", "天龟"],
        BeastType.BIRD: ["青鹰", "金鹏", "雪雁", "彩雀", "朱鹭", "鸾鸟"],
        BeastType.SNAKE: ["白蛇", "青蛇", "赤蛇", "银蛇", "黑蛇", "妖蛇"],
        BeastType.SPIRIT: ["精灵", "仙子", "灵童", "玉女", "星灵", "月灵"],
        BeastType.INSECT: ["玉蝶", "金蜂", "银蝉", "彩蜻", "灵蛾", "星虫"],
    }
    
    # 技能库
    SKILL_POOL = [
        BeastSkill("撕咬", "物理攻击，造成120%伤害", damage_bonus=0.2),
        BeastSkill("爪击", "物理攻击，造成110%伤害", damage_bonus=0.1),
        BeastSkill("冲锋", "快速突袭，伤害提升", damage_bonus=0.15, speed_bonus=0.1),
        BeastSkill("护主", "替主人承受部分伤害", defense_bonus=3),
        BeastSkill("治愈", "战斗中回复主人生命", heal_bonus=10),
        BeastSkill("暴怒", "攻击力大幅提升", damage_bonus=0.3, crit_bonus=0.05),
        BeastSkill("坚固", "防御力提升", defense_bonus=5),
        BeastSkill("闪电", "雷系攻击", damage_bonus=0.25),
        BeastSkill("冰霜", "冰系攻击", damage_bonus=0.2),
        BeastSkill("火焰", "火系攻击", damage_bonus=0.25),
    ]
    
    @staticmethod
    def generate_beast(quality: BeastQuality = None, realm_level: int = 1) -> Beast:
        """生成随机灵兽"""
        # 品质概率
        if quality is None:
            roll = random.random()
            if roll < 0.01:
                quality = BeastQuality.MYTHICAL
            elif roll < 0.05:
                quality = BeastQuality.LEGENDARY
            elif roll < 0.15:
                quality = BeastQuality.ELITE
            elif roll < 0.40:
                quality = BeastQuality.RARE
            else:
                quality = BeastQuality.COMMON
        
        # 生成ID
        beast_id = f"beast_{random.randint(10000, 99999)}"
        
        # 随机类型
        beast_type = random.choice(list(BeastType))
        
        # 生成名字
        name = random.choice(BeastSystem.BEAST_NAMES.get(beast_type, ["灵兽"]))
        
        # 根据品质和境界设置属性
        quality_multiplier = 1.0 + (quality.value - 1) * 0.3
        base_hp = int((40 + realm_level * 8) * quality_multiplier)
        base_attack = int((5 + realm_level * 2) * quality_multiplier)
        base_defense = int((3 + realm_level) * quality_multiplier)
        
        # 创建灵兽
        beast = Beast(
            id=beast_id,
            name=name,
            type=beast_type,
            quality=quality,
            level=realm_level,
            realm="炼气期",
            hp=base_hp,
            max_hp=base_hp,
            qi=base_hp // 2,
            max_qi=base_hp // 2,
            attack=base_attack,
            defense=base_defense,
        )
        
        # 随机技能 (1-3个)
        num_skills = min(3, quality.value)
        beast.skills = random.sample(BeastSystem.SKILL_POOL, num_skills)
        
        # 传说及以上品质有额外加成
        if quality.value >= BeastQuality.LEGENDARY.value:
            beast.crit += 0.05
            beast.speed += 0.1
        
        return beast
    
    @staticmethod
    def contract_beast(player_beasts: List[Beast], player_realm: str) -> Beast:
        """契约灵兽"""
        realm_map = {
            "凡人": 1, "炼气期": 1, "筑基期": 2, "金丹期": 3,
            "元婴期": 4, "化神期": 5, "合体期": 6, "大乘期": 7
        }
        realm_index = realm_map.get(player_realm, 1)
        
        # 高境界有更高概率获得高品质灵兽
        quality_roll = random.random()
        if realm_index >= 5:
            quality = random.choice([BeastQuality.LEGENDARY, BeastQuality.MYTHICAL])
        elif realm_index >= 4:
            quality = random.choice([BeastQuality.ELITE, BeastQuality.LEGENDARY])
        elif realm_index >= 3:
            quality = random.choice([BeastQuality.RARE, BeastQuality.ELITE])
        elif realm_index >= 2:
            quality = random.choice([BeastQuality.COMMON, BeastQuality.RARE])
        else:
            quality = None  # 随机
        
        return BeastSystem.generate_beast(quality, realm_index)
    
    @staticmethod
    def send_to_battle(beast: Beast, enemy_level: int) -> Dict:
        """派遣灵兽战斗"""
        beast.state = BeastState.BATTLE
        
        enemy_hp = 25 + enemy_level * 12
        enemy_attack = 2 + enemy_level * 2
        
        combat_log = []
        
        while beast.hp > 0 and enemy_hp > 0:
            # 灵兽攻击
            damage = beast.attack
            
            # 技能效果
            for skill in beast.skills:
                if skill.damage_bonus > 0:
                    damage = int(damage * (1 + skill.damage_bonus))
            
            # 暴击
            if random.random() < beast.crit:
                damage = int(damage * 1.5)
                combat_log.append(f"暴击! {beast.name}对敌人造成 {damage} 点伤害")
            else:
                combat_log.append(f"{beast.name}对敌人造成 {damage} 点伤害")
            
            enemy_hp -= damage
            
            if enemy_hp <= 0:
                break
            
            # 敌人攻击
            actual_damage = beast.take_damage(enemy_attack)
            combat_log.append(f"敌人对{beast.name}造成 {actual_damage} 点伤害")
        
        beast.state = BeastState.IDLE
        
        if beast.hp > 0:
            # 获得经验
            exp_gain = enemy_level * 10 + 15
            exp_result = beast.gain_experience(exp_gain)
            
            beast.update_intimacy(3)
            
            return {
                "win": True,
                "exp": exp_result["exp_gained"],
                "leveled_up": exp_result["leveled_up"],
                "log": combat_log,
                "evolution_available": exp_result["can_evolution"]
            }
        else:
            beast.update_intimacy(-5)
            return {
                "win": False,
                "exp": 0,
                "log": combat_log
            }
    
    @staticmethod
    def release_beast(beast: Beast) -> str:
        """放生灵兽"""
        return f"灵兽 {beast.name} 已放生，重获自由"
    
    @staticmethod
    def get_beast_summary(beasts: List[Beast]) -> str:
        """获取灵兽概览"""
        if not beasts:
            return "暂无灵兽伙伴"
        
        lines = ["【灵兽伙伴】"]
        for i, b in enumerate(beasts, 1):
            quality_icon = "★" * b.quality.value
            lines.append(f"{i}. {b.name} {quality_icon} - {b.realm}第{b.level}层 (亲密度:{b.intimacy}%)")
        
        return "\n".join(lines)
    
    @staticmethod
    def get_combined_attack(player, beasts: List[Beast], enemy_level: int) -> Dict:
        """玩家与灵兽联手战斗"""
        if not beasts:
            return {"error": "没有灵兽参战"}
        
        # 筛选可战斗的灵兽
        battle_beasts = [b for b in beasts if b.hp > 0 and b.state == BeastState.IDLE]
        
        if not battle_beasts:
            return {"error": "没有可战斗的灵兽"}
        
        enemy_hp = 50 + enemy_level * 20
        enemy_attack = 5 + enemy_level * 3
        
        combat_log = []
        total_damage = 0
        
        # 战斗循环
        round_num = 0
        while player.hp > 0 and enemy_hp > 0:
            round_num += 1
            combat_log.append(f"\n--- 第{round_num}回合 ---")
            
            # 灵兽攻击
            for beast in battle_beasts:
                if beast.hp <= 0:
                    continue
                
                damage = beast.attack
                for skill in beast.skills:
                    if skill.damage_bonus > 0:
                        damage = int(damage * (1 + skill.damage_bonus))
                
                is_crit = random.random() < beast.crit
                if is_crit:
                    damage = int(damage * 1.5)
                    combat_log.append(f"暴击! {beast.name}造成 {damage} 点伤害")
                else:
                    combat_log.append(f"{beast.name}造成 {damage} 点伤害")
                
                enemy_hp -= damage
                total_damage += damage
                
                if enemy_hp <= 0:
                    break
            
            if enemy_hp <= 0:
                break
            
            # 敌人攻击 (分摊给玩家和灵兽)
            for target in [player] + battle_beasts:
                if target.hp <= 0:
                    continue
                    
                if isinstance(target, Beast):
                    actual = target.take_damage(enemy_attack)
                    combat_log.append(f"敌人对{target.name}造成 {actual} 点伤害")
                else:
                    actual = target.take_damage(enemy_attack)
                    combat_log.append(f"敌人对你造成 {actual} 点伤害")
        
        # 战斗结果
        if player.hp > 0:
            exp_gain = enemy_level * 15 + 25
            for beast in battle_beasts:
                beast.gain_experience(exp_gain)
                beast.update_intimacy(2)
            
            reward = enemy_level * 15 + 30
            
            return {
                "win": True,
                "damage_dealt": total_damage,
                "exp": exp_gain,
                "reward": reward,
                "log": combat_log
            }
        else:
            return {
                "win": False,
                "damage_dealt": total_damage,
                "log": combat_log
            }
