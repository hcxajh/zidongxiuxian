"""
修仙游戏核心框架 - 战斗系统 (增强版)
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum
import random
from core.player import Player, Realm
from core.skill import SKILLS_DATABASE, SkillSystem, SkillType
from core.equipment import generate_random_equipment


class CombatState(Enum):
    """战斗状态"""
    IDLE = "idle"
    FIGHTING = "fighting"
    VICTORY = "victory"
    DEFEAT = "defeat"


class BuffType(Enum):
    """增益/减益类型"""
    ATTACK_UP = "attack_up"          # 攻击提升
    ATTACK_DOWN = "attack_down"      # 攻击下降
    DEFENSE_UP = "defense_up"        # 防御提升
    DEFENSE_DOWN = "defense_down"     # 防御下降
    SPEED_UP = "speed_up"            # 速度提升
    SPEED_DOWN = "speed_down"        # 速度下降
    CRIT_UP = "crit_up"              # 暴击提升
    CRIT_DOWN = "crit_down"          # 暴击下降
    SHIELD = "shield"                # 护盾
    REGEN = "regen"                  # 生命恢复
    QI_REGEN = "qi_regen"            # 灵气恢复
    POISON = "poison"                # 中毒
    BURN = "burn"                    # 燃烧
    STUN = "stun"                    # 眩晕
    SILENCE = "silence"              # 沉默
    BLEED = "bleed"                  # 流血
    VULNERABLE = "vulnerable"        # 易伤


@dataclass
class Buff:
    """增益/减益效果"""
    buff_type: BuffType
    value: float
    duration: int  # 持续回合
    source: str = ""  # 来源技能名
    
    def tick(self) -> bool:
        """回合结束时调用，返回是否应该移除"""
        self.duration -= 1
        return self.duration <= 0


@dataclass
class CombatStatus:
    """战斗状态数据"""
    buffs: List[Buff] = field(default_factory=list)
    shield: float = 0.0  # 护盾值
    action_points: int = 1  # 行动点数
    max_action_points: int = 1
    
    def add_buff(self, buff: Buff):
        """添加buff"""
        # 检查是否已存在同类buff，存在则叠加
        for existing in self.buffs:
            if existing.buff_type == buff.buff_type:
                existing.value += buff.value
                existing.duration = max(existing.duration, buff.duration)
                return
        self.buffs.append(buff)
    
    def remove_buff(self, buff_type: BuffType):
        """移除buff"""
        self.buffs = [b for b in self.buffs if b.buff_type != buff_type]
    
    def get_buff_value(self, buff_type: BuffType) -> float:
        """获取buff值"""
        for buff in self.buffs:
            if buff.buff_type == buff_type:
                return buff.value
        return 0.0
    
    def has_buff(self, buff_type: BuffType) -> bool:
        """是否有某类buff"""
        return any(b.buff_type == buff_type for b in self.buffs)
    
    def tick_buffs(self) -> List[str]:
        """回合结束处理buff，返回触发的事件列表"""
        events = []
        to_remove = []
        
        for buff in self.buffs:
            # 每回合结束的效果
            if buff.buff_type == BuffType.REGEN:
                events.append(f"生命恢复 +{buff.value:.1f}")
            elif buff.buff_type == BuffType.QI_REGEN:
                events.append(f"灵气恢复 +{buff.value:.1f}")
            elif buff.buff_type == BuffType.POISON:
                events.append(f"中毒受到 {buff.value:.1f} 伤害")
            elif buff.buff_type == BuffType.BURN:
                events.append(f"燃烧受到 {buff.value:.1f} 伤害")
            elif buff.buff_type == BuffType.BLEED:
                events.append(f"流血受到 {buff.value:.1f} 伤害")
            
            # 减少持续时间
            if buff.tick():
                to_remove.append(buff)
        
        for buff in to_remove:
            self.buffs.remove(buff)
        
        return events
    
    def clear_debuffs(self):
        """清除减益"""
        self.buffs = [b for b in self.buffs if not self._is_debuff(b.buff_type)]
    
    @staticmethod
    def _is_debuff(buff_type: BuffType) -> bool:
        """是否是减益"""
        debuffs = {
            BuffType.ATTACK_DOWN, BuffType.DEFENSE_DOWN, 
            BuffType.SPEED_DOWN, BuffType.CRIT_DOWN,
            BuffType.POISON, BuffType.BURN, BuffType.STUN,
            BuffType.SILENCE, BuffType.BLEED, BuffType.VULNERABLE
        }
        return buff_type in debuffs


class CombatAction:
    """战斗行动"""
    
    ATTACK = "attack"           # 普通攻击
    SKILL = "skill"             # 使用技能
    DEFEND = "defend"           # 防御
    DODGE = "dodge"             # 闪避
    CHARGE = "charge"           # 蓄力
    ESCAPE = "escape"           # 逃跑
    ITEM = "item"               # 使用物品


@dataclass
class Enemy:
    """敌人"""
    name: str
    realm: Realm
    level: int
    hp: float
    max_hp: float
    attack: int
    defense: int
    qi: float = 0.0
    drops: dict = None  # 掉落
    
    # 战斗属性
    crit: float = 0.1          # 暴击率
    speed: float = 1.0         # 速度
    dodge: float = 0.1         # 闪避率
    element: str = ""          # 元素属性
    
    # 战斗状态
    combat_status: CombatStatus = field(default_factory=CombatStatus)
    ai_type: str = "normal"    # AI类型: normal, aggressive, defensive, healer
    
    def __post_init__(self):
        if self.drops is None:
            self.drops = {}
        if self.combat_status is None:
            self.combat_status = CombatStatus()


class Combat:
    """战斗系统增强版"""
    
    # 暴击伤害倍率
    CRIT_MULTIPLIER = 1.5
    
    # 闪避成功伤害减免
    DODGE_REDUCTION = 1.0
    
    # 防御减伤比例
    DEFENSE_RATIO = 0.5
    
    @staticmethod
    def create_enemy(realm: Realm, level: int = 1) -> Enemy:
        """根据境界创建敌人"""
        enemies_data = {
            Realm.MORTAL: [
                ("山贼", 50, 5, 2, "normal"),
                ("野狼", 40, 6, 1, "aggressive"),
                ("毒蛇", 35, 8, 1, "aggressive"),
                ("盗墓贼", 55, 4, 3, "defensive"),
            ],
            Realm.QI_REFINING: [
                ("炼气修士", 80, 12, 8, "normal"),
                ("妖狼", 70, 14, 10, "aggressive"),
                ("火狐", 65, 16, 8, "aggressive"),
                ("冰蝉", 75, 10, 12, "healer"),
            ],
            Realm.FOUNDATION: [
                ("筑基修士", 150, 25, 20, "normal"),
                ("妖蛇", 130, 28, 18, "aggressive"),
                ("铁甲熊", 180, 20, 25, "defensive"),
                ("幽魂", 100, 35, 15, "aggressive"),
            ],
            Realm.GOLDEN_CORE: [
                ("金丹修士", 300, 50, 40, "normal"),
                ("蛟龙", 280, 55, 50, "aggressive"),
                ("雷凤", 250, 60, 35, "aggressive"),
                ("玄龟", 350, 40, 60, "defensive"),
            ],
            Realm.NASENT_SOUL: [
                ("元婴老怪", 500, 80, 70, "normal"),
                ("域外天魔", 450, 95, 60, "aggressive"),
                ("万年古魔", 550, 70, 90, "defensive"),
            ],
        }
        
        enemy_list = enemies_data.get(realm, [("筑基修士", 150, 25, 20, "normal")])
        name, hp, atk, dfs, ai = random.choice(enemy_list)
        
        # 装备掉落概率
        drop_equipment = random.random() < 0.3
        
        drops = {}
        if drop_equipment:
            drops["equipment"] = True
        
        # 随机元素属性
        elements = ["", "金", "木", "水", "火", "土", "雷", "冰"]
        element = random.choice(elements) if random.random() < 0.4 else ""
        
        return Enemy(
            name=f"{name}{level}层",
            realm=realm,
            level=level,
            hp=hp * level * 0.5,
            max_hp=hp * level * 0.5,
            attack=atk + level * 2,
            defense=dfs + level,
            drops=drops,
            element=element,
            ai_type=ai,
        )
    
    @staticmethod
    def calculate_damage(
        attacker_atk: int, 
        defender_def: int, 
        skill_bonus: float = 1.0,
        realm_bonus: float = 1.0,
        is_crit: bool = False,
        element_match: float = 1.0,
        true_damage: float = 0.0
    ) -> float:
        """伤害计算"""
        base = attacker_atk - defender_def * Combat.DEFENSE_RATIO
        
        # 真实伤害直接加成
        if true_damage > 0:
            base = true_damage
        
        # 随机波动
        damage = max(base * random.uniform(0.8, 1.2), 1.0)
        
        # 暴击加成
        if is_crit:
            damage *= Combat.CRIT_MULTIPLIER
        
        # 技能加成
        damage *= skill_bonus
        
        # 境界加成
        damage *= realm_bonus
        
        # 元素契合
        damage *= element_match
        
        return max(damage, 1.0)
    
    @staticmethod
    def check_hit(dodge_rate: float, accuracy: float = 1.0) -> bool:
        """命中判定"""
        hit_chance = 1.0 - dodge_rate * accuracy
        return random.random() < hit_chance
    
    @staticmethod
    def check_crit(crit_rate: float) -> bool:
        """暴击判定"""
        return random.random() < min(crit_rate, 0.95)
    
    @staticmethod
    def resolve_attack(
        attacker: Player,
        defender: Enemy,
        skill_damage: float = 0,
        skill_bonus: float = 1.0,
        true_damage: float = 0.0,
        element: str = "",
        buffs: List[Buff] = None
    ) -> dict:
        """
        执行一次攻击
        返回攻击结果详情
        """
        result = {
            "hit": True,
            "crit": False,
            "damage": 0,
            "element": element,
            "buffs": [],
            "message": ""
        }
        
        # 获取攻击者buff加成
        attack_bonus = 1.0 + attacker.combat_status.get_buff_value(BuffType.ATTACK_UP) if hasattr(attacker, 'combat_status') else 1.0
        
        # 检查命中
        accuracy = 1.0
        if not Combat.check_hit(defender.dodge, accuracy):
            result["hit"] = False
            result["message"] = f"{defender.name}闪避了攻击!"
            return result
        
        # 检查暴击
        is_crit = Combat.check_crit(attacker.crit)
        if is_crit:
            result["crit"] = True
        
        # 计算元素加成
        element_match = 1.0
        if element and defender.element:
            from core.element import ElementSystem
            element_match = ElementSystem.get_element_advantage(element, defender.element)
        
        # 计算伤害
        base_attack = attacker.attack * attack_bonus
        total_damage = Combat.calculate_damage(
            attacker_atk=base_attack + skill_damage,
            defender_def=defender.defense,
            skill_bonus=skill_bonus,
            is_crit=is_crit,
            element_match=element_match,
            true_damage=true_damage
        )
        
        # 护盾减免
        shield = defender.combat_status.shield
        if shield > 0:
            if shield >= total_damage:
                defender.combat_status.shield = shield - total_damage
                total_damage = 0
                result["message"] = f"护盾吸收了全部伤害!"
            else:
                defender.combat_status.shield = 0
                total_damage -= shield
                result["message"] = f"护盾破碎，伤害-{shield:.1f}!"
        
        # 施加debuff
        if buffs:
            for buff in buffs:
                defender.combat_status.add_buff(buff)
                result["buffs"].append(buff.buff_type.value)
        
        result["damage"] = max(total_damage, 0)
        defender.hp -= result["damage"]
        
        # 伤害消息
        if result["hit"]:
            msg = f"对{defender.name}造成 {result['damage']:.1f} 伤害"
            if result["crit"]:
                msg += " (暴击!)"
            if element:
                msg += f" [{element}]"
            result["message"] = msg
        
        return result
    
    @staticmethod
    def enemy_attack(
        enemy: Enemy,
        player: Player,
        realm_bonus: float = 1.0
    ) -> dict:
        """敌人攻击玩家"""
        result = {
            "hit": True,
            "crit": False,
            "damage": 0,
            "message": ""
        }
        
        # 检查玩家防御姿态
        is_defending = player.combat_status.has_buff(BuffType.SHIELD) if hasattr(player, 'combat_status') else False
        
        # 检查闪避
        player_dodge = 0.1 + player.combat_status.get_buff_value(BuffType.SPEED_UP) if hasattr(player, 'combat_status') else 0.1
        if not Combat.check_hit(player_dodge):
            result["hit"] = False
            result["message"] = f"你闪避了{enemy.name}的攻击!"
            return result
        
        # 基础伤害
        base_damage = enemy.attack
        
        # 玩家防御减伤
        defense_reduction = 1.0
        if is_defending:
            defense_reduction = 0.3
            result["message"] = "防御姿态减免70%伤害!"
        
        # 玩家防御buff
        defense_bonus = player.combat_status.get_buff_value(BuffType.DEFENSE_UP) if hasattr(player, 'combat_status') else 0
        final_defense = player.defense + defense_bonus
        
        damage = max(base_damage - final_defense * Combat.DEFENSE_RATIO, 1.0) * defense_reduction * realm_bonus
        
        # 玩家护盾
        shield = player.combat_status.shield if hasattr(player, 'combat_status') else 0
        if shield > 0:
            if shield >= damage:
                player.combat_status.shield = shield - damage
                damage = 0
                result["message"] += " 护盾吸收了伤害!"
            else:
                player.combat_status.shield = 0
                damage -= shield
        
        # 玩家扣血
        if damage > 0:
            player.hp -= damage
            player.consume_qi(damage * 0.3)  # 受伤消耗灵气
        
        result["damage"] = damage
        result["message"] = f"{enemy.name}对你造成 {damage:.1f} 伤害" + (f". {result['message']}" if result["message"] else "!")
        
        return result
    
    @staticmethod
    def battle(player, enemy: Enemy, auto: bool = True) -> tuple[bool, str]:
        """
        战斗
        返回: (是否胜利, 战斗日志)
        """
        # 初始化战斗状态
        if not hasattr(player, 'combat_status'):
            player.combat_status = CombatStatus()
        enemy.combat_status = CombatStatus()
        
        log = []
        log.append(f"\n{'='*50}")
        log.append(f"=== 战斗开始: {player.name} vs {enemy.name} ===")
        log.append(f"敌人信息: 生命{enemy.max_hp:.0f} 攻击{enemy.attack} 防御{enemy.defense}")
        if enemy.element:
            log.append(f"敌人属性: {enemy.element}")
        log.append(f"{'='*50}")
        
        # 计算境界压制
        suppression = Player.get_realm_suppression(player.realm, enemy.realm)
        player_bonus = suppression["bonus"]
        
        # 显示境界压制信息
        if player_bonus > 1.0:
            realm_diff = list(Realm).index(player.realm) - list(Realm).index(enemy.realm)
            log.append(f"【境界压制】你比敌人高 {realm_diff} 阶，伤害+{((player_bonus-1)*100):.0f}%")
        elif player_bonus < 1.0:
            realm_diff = list(Realm).index(enemy.realm) - list(Realm).index(player.realm)
            log.append(f"【境界压制】敌人比你高 {realm_diff} 阶，伤害-{((1-player_bonus)*100):.0f}%")
        
        round_num = 0
        while player.qi > 0 and player.hp > 0 and enemy.hp > 0:
            round_num += 1
            log.append(f"\n--- 第{round_num}回合 ---")
            
            # 玩家行动
            # 检查是否被沉默
            is_silenced = player.combat_status.has_buff(BuffType.SILENCE) if hasattr(player, 'combat_status') else False
            is_stunned = player.combat_status.has_buff(BuffType.STUN) if hasattr(player, 'combat_status') else False
            
            if is_stunned:
                log.append("【你被眩晕了，无法行动!】")
            else:
                # 玩家普通攻击
                player_dmg = Combat.calculate_damage(player.attack, enemy.defense, realm_bonus=player_bonus)
                enemy.hp -= player_dmg
                log.append(f"你对{enemy.name}造成 {player_dmg:.1f} 伤害")
                
                # 尝试使用技能 (如果有)
                if not is_silenced and player.skills:
                    # 选择一个攻击技能使用
                    for skill_id, pskill in player.skills.items():
                        skill = SKILLS_DATABASE.get(skill_id)
                        if skill and skill.type == SkillType.ATTACK:
                            if player.qi >= skill.qi_cost:
                                # 使用技能
                                result = SkillSystem.use_skill(skill_id, player)
                                if result["success"] and result.get("damage", 0) > 0:
                                    # 技能伤害
                                    skill_dmg = result["damage"] * player_bonus
                                    enemy.hp -= skill_dmg
                                    log.append(f"使用【{skill.name}】对{enemy.name}造成 {skill_dmg:.1f} 伤害!")
                                    break
            
            if enemy.hp <= 0:
                break
            
            # 敌人行动 (AI)
            enemy_turn_log = Combat.enemy_turn(enemy, player, player_bonus)
            log.extend(enemy_turn_log)
            
            # 回合结束处理
            # 玩家buff结算
            if hasattr(player, 'combat_status'):
                buff_events = player.combat_status.tick_buffs()
                for event in buff_events:
                    if "恢复" in event:
                        if "生命" in event:
                            player.heal(player.combat_status.get_buff_value(BuffType.REGEN))
                        elif "灵气" in event:
                            player.gain_qi(player.combat_status.get_buff_value(BuffType.QI_REGEN))
                    elif "伤害" in event:
                        dmg = float(event.split()[-1])
                        player.hp -= dmg
                        player.consume_qi(dmg * 0.3)
                
                # 护盾每回合衰减
                if player.combat_status.shield > 0:
                    player.combat_status.shield *= 0.9
            
            # 敌人buff结算
            buff_events = enemy.combat_status.tick_buffs()
            
            # 减少冷却
            player.tick_cooldowns()
            
            # 显示当前状态
            log.append(f"【你】生命:{player.hp:.1f}/{player.max_hp:.1f} 灵气:{player.qi:.1f}/{player.max_qi:.1f}")
            log.append(f"【敌】生命:{enemy.hp:.1f}/{enemy.max_hp:.1f}")
        
        # 战斗结果
        log.append(f"\n{'='*50}")
        if enemy.hp <= 0:
            # 胜利奖励
            spirit_stones = random.randint(10, 50) * (enemy.level + 1)
            if player_bonus > 1.0:
                spirit_stones = int(spirit_stones * player_bonus)
            player.spirit_stones += spirit_stones
            log.append(f"✓ 战斗胜利! 获得灵石: {spirit_stones}")
            
            # 装备掉落
            if enemy.drops.get("equipment"):
                realm_level = list(Realm).index(player.realm) + 1
                equip = generate_random_equipment(realm_level)
                
                if player.level >= equip.level_required:
                    log.append(f"★ 装备掉落: {equip.name} ({equip.quality.name})")
                    log.append(f"  属性: {equip.total_stats.to_dict()}")
                    
                    if not hasattr(player, 'inventory'):
                        player.inventory = []
                    player.inventory.append(equip)
                    log.append(f"  已放入背包")
                else:
                    log.append(f"★ 装备掉落: {equip.name} (等级不足，无法装备)")
            
            if player.qi < 0:
                player.qi = 0
                
            return True, "\n".join(log)
        else:
            log.append(f"✗ 战斗失败! 生命耗尽")
            if player.qi < 0:
                player.qi = 0
            return False, "\n".join(log)
    
    @staticmethod
    def enemy_turn(enemy: Enemy, player: Player, realm_bonus: float = 1.0) -> List[str]:
        """敌人AI行动"""
        log = []
        
        # 根据AI类型决定行动
        action = Combat.choose_enemy_action(enemy, player)
        
        if action == "attack":
            result = Combat.enemy_attack(enemy, player, realm_bonus)
            log.append(result["message"])
        elif action == "defend":
            enemy.combat_status.add_buff(Buff(BuffType.DEFENSE_UP, 0.3, 1, "防御"))
            log.append(f"{enemy.name}进入防御姿态")
        elif action == "buff":
            buff_types = [BuffType.ATTACK_UP, BuffType.DEFENSE_UP]
            buff = random.choice(buff_types)
            enemy.combat_status.add_buff(Buff(buff, 0.2, 2, "强化"))
            log.append(f"{enemy.name}使用了强化技能")
        elif action == "heal" and enemy.ai_type == "healer":
            heal_amount = enemy.max_hp * 0.2
            enemy.hp = min(enemy.max_hp, enemy.hp + heal_amount)
            log.append(f"{enemy.name}恢复了 {heal_amount:.1f} 生命")
        
        return log
    
    @staticmethod
    def choose_enemy_action(enemy: Enemy, player: Player) -> str:
        """敌人AI选择行动"""
        hp_ratio = enemy.hp / enemy.max_hp
        
        if enemy.ai_type == "aggressive":
            return "attack"
        elif enemy.ai_type == "defensive":
            if hp_ratio < 0.5:
                return "defend"
            return "attack"
        elif enemy.ai_type == "healer":
            if hp_ratio < 0.6:
                return "heal"
            return "attack"
        else:
            # normal AI
            if hp_ratio < 0.3:
                return random.choice(["defend", "attack"])
            return "attack"
