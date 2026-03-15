"""
修仙游戏核心框架 - 历练副本系统
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import random
from core.player import Player, Realm
from core.combat import Enemy, Combat


class AdventureType(Enum):
    """历练类型"""
    DUNGEON = "副本"          # 地下城类型
    TRIAL = "试炼"            # 试炼塔类型
    SECRET_REALM = "秘境"     # 秘境界限
    BOSS_RAID = "Boss讨伐"    # Boss讨伐


class AdventureEventType(Enum):
    """历练事件类型"""
    ENEMY = "敌人"
    TREASURE = "宝箱"
    REST = "休息区"
    TRAP = "陷阱"
    MYSTERY = "神秘商人"
    ELITE = "精英怪"
    BOSS = "Boss"


@dataclass
class AdventureEvent:
    """历练事件"""
    event_type: AdventureEventType
    name: str
    description: str
    enemy_data: Optional[Dict] = None  # 敌人配置
    reward_data: Optional[Dict] = None  # 奖励配置
    difficulty_modifier: float = 1.0  # 难度修正


@dataclass
class AdventureWave:
    """历练波次"""
    wave_number: int
    events: List[AdventureEvent]
    is_boss_wave: bool = False


@dataclass
class AdventureProgress:
    """历练进度"""
    adventure_id: str
    current_wave: int = 0
    current_event_index: int = 0
    events_completed: List[str] = field(default_factory=list)
    total_damage_dealt: float = 0.0
    total_damage_taken: float = 0.0
    enemies_defeated: int = 0
    is_completed: bool = False
    is_failed: bool = False


@dataclass
class AdventureReward:
    """历练奖励"""
    spirit_stones: Tuple[int, int]  # (min, max)
    cultivation: Tuple[int, int]    # 修为 (min, max)
    items: List[str] = field(default_factory=list)
    equipment_drop_chance: float = 0.0


class AdventureSystem:
    """历练副本系统"""
    
    # ============ 历练配置 ============
    
    # 历练事件模板
    EVENT_TEMPLATES = {
        AdventureEventType.ENEMY: [
            {"name": "巡逻修士", "base_hp": 50, "base_atk": 10},
            {"name": "守护灵兽", "base_hp": 80, "base_atk": 15},
            {"name": "邪修弟子", "base_hp": 60, "base_atk": 12},
            {"name": "妖物", "base_hp": 70, "base_atk": 14},
        ],
        AdventureEventType.ELITE: [
            {"name": "精英护卫", "base_hp": 150, "base_atk": 25},
            {"name": "千年妖王", "base_hp": 200, "base_atk": 30},
            {"name": "魔道修士", "base_hp": 180, "base_atk": 28},
        ],
        AdventureEventType.BOSS: [
            {"name": "守护长老", "base_hp": 500, "base_atk": 50},
            {"name": "上古妖皇", "base_hp": 800, "base_atk": 70},
            {"name": "魔尊分身", "base_hp": 1000, "base_atk": 80},
            {"name": "洞府主人", "base_hp": 600, "base_atk": 60},
        ],
        AdventureEventType.TREASURE: [
            {"name": "灵石宝箱", "min_stones": 50, "max_stones": 200},
            {"name": "灵药宝箱", "items": ["spiritual_herb"]},
            {"name": "装备宝箱", "equipment": True},
        ],
        AdventureEventType.REST: [
            {"name": "灵气泉眼", "qi_restore": 50},
            {"name": "安全营地", "hp_restore": 30},
        ],
        AdventureEventType.TRAP: [
            {"name": "机关陷阱", "damage": 30},
            {"name": "幻阵", "qi_drain": 40},
        ],
        AdventureEventType.MYSTERY: [
            {"name": "神秘商人", "discount": 0.8},
            {"name": "隐世高人", "teach_skill": True},
        ],
    }
    
    # 每种历练类型的波次配置
    WAVE_CONFIG = {
        AdventureType.DUNGEON: {
            "wave_count": 5,
            "events_per_wave": 3,
            "boss_on_last_wave": True,
        },
        AdventureType.TRIAL: {
            "wave_count": 10,
            "events_per_wave": 1,
            "boss_on_last_wave": True,
        },
        AdventureType.SECRET_REALM: {
            "wave_count": 7,
            "events_per_wave": 2,
            "boss_on_last_wave": True,
        },
        AdventureType.BOSS_RAID: {
            "wave_count": 1,
            "events_per_wave": 1,
            "boss_on_last_wave": True,
        },
    }
    
    @staticmethod
    def generate_adventure_events(
        adventure_type: AdventureType,
        player: Player,
        difficulty: float = 1.0
    ) -> List[AdventureWave]:
        """生成历练事件"""
        config = AdventureSystem.WAVE_CONFIG[adventure_type]
        waves = []
        
        realm_index = list(Realm).index(player.realm)
        
        for wave_num in range(1, config["wave_count"] + 1):
            events = []
            is_boss_wave = wave_num == config["wave_count"] and config["boss_on_last_wave"]
            
            # 难度随波次增加
            wave_difficulty = difficulty * (1 + (wave_num - 1) * 0.2)
            
            for event_idx in range(config["events_per_wave"]):
                event = AdventureSystem._generate_single_event(
                    player, wave_difficulty, is_boss_wave, event_idx
                )
                if event:
                    events.append(event)
            
            waves.append(AdventureWave(
                wave_number=wave_num,
                events=events,
                is_boss_wave=is_boss_wave
            ))
        
        return waves
    
    @staticmethod
    def _generate_single_event(
        player: Player,
        difficulty: float,
        is_boss_wave: bool,
        event_index: int
    ) -> Optional[AdventureEvent]:
        """生成单个事件"""
        
        # 根据波次和索引决定事件类型
        if is_boss_wave:
            # 最后一波是Boss
            boss_templates = AdventureSystem.EVENT_TEMPLATES[AdventureEventType.BOSS]
            template = random.choice(boss_templates)
            
            realm_index = list(Realm).index(player.realm)
            hp_multiplier = (realm_index + 1) * difficulty * 2
            atk_multiplier = (realm_index + 1) * difficulty * 1.5
            
            return AdventureEvent(
                event_type=AdventureEventType.BOSS,
                name=template["name"],
                description=f"强大的{template['name']}挡住了去路",
                enemy_data={
                    "name": template["name"],
                    "hp": template["base_hp"] * hp_multiplier,
                    "attack": int(template["base_atk"] * atk_multiplier),
                    "defense": int(10 * difficulty),
                },
                difficulty_modifier=difficulty * 2,
            )
        
        elif event_index == 0 and random.random() < 0.3:
            # 30%概率遇到精英怪
            elite_templates = AdventureSystem.EVENT_TEMPLATES[AdventureEventType.ELITE]
            template = random.choice(elite_templates)
            
            realm_index = list(Realm).index(player.realm)
            hp_multiplier = (realm_index + 1) * difficulty * 1.2
            atk_multiplier = (realm_index + 1) * difficulty * 1.2
            
            return AdventureEvent(
                event_type=AdventureEventType.ELITE,
                name=template["name"],
                description=f"遭遇{template['name']}的拦截",
                enemy_data={
                    "name": template["name"],
                    "hp": template["base_hp"] * hp_multiplier,
                    "attack": int(template["base_atk"] * atk_multiplier),
                    "defense": int(5 * difficulty),
                },
                difficulty_modifier=difficulty * 1.5,
            )
        
        else:
            # 普通事件
            event_weights = [
                (AdventureEventType.ENEMY, 50),
                (AdventureEventType.TREASURE, 20),
                (AdventureEventType.REST, 15),
                (AdventureEventType.TRAP, 10),
                (AdventureEventType.MYSTERY, 5),
            ]
            
            # 根据权重随机选择
            total_weight = sum(w for _, w in event_weights)
            rand = random.randint(1, total_weight)
            
            cumulative = 0
            selected_type = AdventureEventType.ENEMY
            for etype, weight in event_weights:
                cumulative += weight
                if rand <= cumulative:
                    selected_type = etype
                    break
            
            return AdventureSystem._create_normal_event(selected_type, player, difficulty)
    
    @staticmethod
    def _create_normal_event(
        event_type: AdventureEventType,
        player: Player,
        difficulty: float
    ) -> AdventureEvent:
        """创建普通事件"""
        
        if event_type == AdventureEventType.ENEMY:
            templates = AdventureSystem.EVENT_TEMPLATES[AdventureEventType.ENEMY]
            template = random.choice(templates)
            realm_index = list(Realm).index(player.realm)
            
            hp_multiplier = (realm_index + 1) * difficulty
            atk_multiplier = (realm_index + 1) * difficulty
            
            return AdventureEvent(
                event_type=event_type,
                name=template["name"],
                description=f"遭遇{template['name']}的袭击",
                enemy_data={
                    "name": template["name"],
                    "hp": template["base_hp"] * hp_multiplier,
                    "attack": int(template["base_atk"] * atk_multiplier),
                    "defense": int(3 * difficulty),
                },
                difficulty_modifier=difficulty,
            )
        
        elif event_type == AdventureEventType.TREASURE:
            templates = AdventureSystem.EVENT_TEMPLATES[AdventureEventType.TREASURE]
            template = random.choice(templates)
            
            return AdventureEvent(
                event_type=event_type,
                name=template["name"],
                description=f"发现{template['name']}",
                reward_data=template,
                difficulty_modifier=0,
            )
        
        elif event_type == AdventureEventType.REST:
            templates = AdventureSystem.EVENT_TEMPLATES[AdventureEventType.REST]
            template = random.choice(templates)
            
            return AdventureEvent(
                event_type=event_type,
                name=template["name"],
                description=f"发现{template['name']}，可以恢复状态",
                reward_data=template,
                difficulty_modifier=0,
            )
        
        elif event_type == AdventureEventType.TRAP:
            templates = AdventureSystem.EVENT_TEMPLATES[AdventureEventType.TRAP]
            template = random.choice(templates)
            
            return AdventureEvent(
                event_type=event_type,
                name=template["name"],
                description=f"触发{template['name']}",
                reward_data=template,
                difficulty_modifier=0,
            )
        
        elif event_type == AdventureEventType.MYSTERY:
            templates = AdventureSystem.EVENT_TEMPLATES[AdventureEventType.MYSTERY]
            template = random.choice(templates)
            
            return AdventureEvent(
                event_type=event_type,
                name=template["name"],
                description=f"偶遇{template['name']}",
                reward_data=template,
                difficulty_modifier=0,
            )
        
        # 默认敌人事件
        return AdventureSystem._create_normal_event(AdventureEventType.ENEMY, player, difficulty)
    
    @staticmethod
    def calculate_rewards(
        waves: List[AdventureWave],
        progress: AdventureProgress,
        player: Player
    ) -> Dict:
        """计算历练奖励"""
        # 基础奖励
        base_stones = 50 * (list(Realm).index(player.realm) + 1)
        base_cultivation = 20 * (list(Realm).index(player.realm) + 1)
        
        # 根据完成度计算
        total_events = sum(len(w.events) for w in waves)
        completion_ratio = progress.enemies_defeated / max(1, total_events)
        
        # 波次完成奖励
        wave_bonus = progress.current_wave * 20
        
        spirit_stones = int((base_stones + wave_bonus) * completion_ratio)
        cultivation = int((base_cultivation + wave_bonus) * completion_ratio)
        
        # 完美通关奖励
        items = []
        if progress.is_completed:
            if progress.enemies_defeated >= len(waves) * 3:  # 击败所有敌人
                items.append("perfect_clear_bonus")
        
        return {
            "spirit_stones": spirit_stones,
            "cultivation": cultivation,
            "items": items,
        }
    
    @staticmethod
    def start_adventure(
        player: Player,
        adventure_type: AdventureType,
        difficulty: float = 1.0
    ) -> Tuple[List[AdventureWave], AdventureProgress]:
        """开始历练"""
        waves = AdventureSystem.generate_adventure_events(adventure_type, player, difficulty)
        
        progress = AdventureProgress(
            adventure_id=adventure_type.value,
            current_wave=1,
            current_event_index=0,
        )
        
        return waves, progress
    
    @staticmethod
    def process_event(
        player: Player,
        event: AdventureEvent,
        waves: List[AdventureWave],
        progress: AdventureProgress
    ) -> Dict:
        """处理历练事件"""
        log = []
        
        if event.event_type in [AdventureEventType.ENEMY, 
                                  AdventureEventType.ELITE, 
                                  AdventureEventType.BOSS]:
            # 战斗事件
            result = AdventureSystem._process_combat(player, event, log)
            if result["victory"]:
                progress.enemies_defeated += 1
                
                # 战斗奖励
                stones = random.randint(10, 30) * event.difficulty_modifier
                player.spirit_stones += int(stones)
                log.append(f"战斗胜利! 获得{int(stones)}灵石")
            
            progress.total_damage_dealt += result.get("damage_dealt", 0)
            progress.total_damage_taken += result.get("damage_taken", 0)
        
        elif event.event_type == AdventureEventType.TREASURE:
            # 宝箱事件
            result = AdventureSystem._process_treasure(player, event, log)
        
        elif event.event_type == AdventureEventType.REST:
            # 休息事件
            result = AdventureSystem._process_rest(player, event, log)
        
        elif event.event_type == AdventureEventType.TRAP:
            # 陷阱事件
            result = AdventureSystem._process_trap(player, event, log)
        
        elif event.event_type == AdventureEventType.MYSTERY:
            # 神秘事件
            result = AdventureSystem._process_mystery(player, event, log)
        
        else:
            result = {"success": True, "message": "事件处理完成"}
        
        # 记录完成的事件
        progress.events_completed.append(event.name)
        
        return result
    
    @staticmethod
    def _process_combat(player: Player, event: AdventureEvent, log: List[str]) -> Dict:
        """处理战斗事件"""
        enemy_data = event.enemy_data
        
        # 创建敌人
        enemy = Enemy(
            name=enemy_data["name"],
            realm=player.realm,
            level=player.level,
            hp=enemy_data["hp"],
            max_hp=enemy_data["hp"],
            attack=enemy_data["attack"],
            defense=enemy_data["defense"],
        )
        
        log.append(f"\n{'='*40}")
        log.append(f"【{event.event_type.value}】{enemy.name}")
        log.append(f"HP: {enemy.hp:.0f} | 攻击: {enemy.attack} | 防御: {enemy.defense}")
        log.append(f"{'='*40}")
        
        # 记录伤害
        total_damage_dealt = 0
        total_damage_taken = 0
        
        # 战斗循环
        round_num = 0
        while player.qi > 0 and enemy.hp > 0:
            round_num += 1
            
            # 玩家攻击
            player_dmg = Combat.calculate_damage(player.attack, enemy.defense)
            enemy.hp -= player_dmg
            total_damage_dealt += player_dmg
            
            log.append(f"\n第{round_num}回合:")
            log.append(f"  你对{enemy.name}造成 {player_dmg:.1f} 伤害 (敌人HP: {max(0, enemy.hp):.0f})")
            
            if enemy.hp <= 0:
                break
            
            # 敌人攻击
            enemy_dmg = Combat.calculate_damage(enemy.attack, player.defense)
            player.consume_qi(enemy_dmg * 0.5)
            total_damage_taken += enemy_dmg
            
            log.append(f"  {enemy.name}对你造成 {enemy_dmg:.1f} 伤害 (灵气-{enemy_dmg*0.5:.1f})")
            
            # 检查是否失败
            if player.qi <= 0:
                log.append(f"\n灵气耗尽! 战斗失败!")
                return {
                    "victory": False,
                    "damage_dealt": total_damage_dealt,
                    "damage_taken": total_damage_taken,
                    "log": "\n".join(log),
                }
        
        # 胜利
        log.append(f"\n★★★ 战斗胜利! 击败了{enemy.name} ★★★")
        
        return {
            "victory": True,
            "damage_dealt": total_damage_dealt,
            "damage_taken": total_damage_taken,
            "log": "\n".join(log),
        }
    
    @staticmethod
    def _process_treasure(player: Player, event: AdventureEvent, log: List[str]) -> Dict:
        """处理宝箱事件"""
        reward = event.reward_data
        
        log.append(f"\n开启{event.name}...")
        
        stones = 0
        if "min_stones" in reward:
            stones = random.randint(reward["min_stones"], reward["max_stones"])
            player.spirit_stones += stones
            log.append(f"  获得灵石: {stones}")
        
        if "items" in reward:
            items = reward["items"]
            log.append(f"  获得物品: {', '.join(items)}")
            # 实际奖励会在后面统一发放
        
        if reward.get("equipment"):
            from core.equipment import generate_random_equipment
            realm_level = list(Realm).index(player.realm) + 1
            equip = generate_random_equipment(realm_level)
            if not hasattr(player, 'inventory'):
                player.inventory = []
            player.inventory.append(equip)
            log.append(f"  获得装备: {equip.name}")
        
        return {"success": True, "log": "\n".join(log)}
    
    @staticmethod
    def _process_rest(player: Player, event: AdventureEvent, log: List[str]) -> Dict:
        """处理休息事件"""
        reward = event.reward_data
        
        log.append(f"\n{event.name}:")
        
        if "qi_restore" in reward:
            restore = reward["qi_restore"]
            player.qi = min(player.max_qi, player.qi + restore)
            log.append(f"  灵气恢复: +{restore}")
        
        if "hp_restore" in reward:
            restore = reward["hp_restore"]
            # 假设hp和max_hp属性存在
            if hasattr(player, 'hp'):
                player.hp = min(player.max_hp, player.hp + restore)
                log.append(f"  气血恢复: +{restore}")
        
        return {"success": True, "log": "\n".join(log)}
    
    @staticmethod
    def _process_trap(player: Player, event: AdventureEvent, log: List[str]) -> Dict:
        """处理陷阱事件"""
        reward = event.reward_data
        
        log.append(f"\n触发{event.name}!")
        
        if "damage" in reward:
            damage = reward["damage"]
            player.consume_qi(damage)
            log.append(f"  受到伤害: {damage}点灵气")
        
        if "qi_drain" in reward:
            drain = reward["qi_drain"]
            player.qi = max(0, player.qi - drain)
            log.append(f"  灵气流失: {drain}点")
        
        return {"success": True, "log": "\n".join(log)}
    
    @staticmethod
    def _process_mystery(player: Player, event: AdventureEvent, log: List[str]) -> Dict:
        """处理神秘事件"""
        reward = event.reward_data
        
        log.append(f"\n{event.name}出现!")
        
        if "discount" in reward:
            log.append(f"  神秘商人提供{reward['discount']*100:.0f}折优惠")
            # 可以在后续实现商店功能
        
        if reward.get("teach_skill"):
            log.append("  隐世高人指点修为，修炼速度提升")
            player.cultivation_speed *= 1.1
        
        return {"success": True, "log": "\n".join(log)}
    
    @staticmethod
    def advance_event(
        waves: List[AdventureWave],
        progress: AdventureProgress
    ) -> Optional[AdventureEvent]:
        """获取下一个事件"""
        if progress.current_wave > len(waves):
            progress.is_completed = True
            return None
        
        wave = waves[progress.current_wave - 1]
        
        if progress.current_event_index >= len(wave.events):
            # 进入下一波
            progress.current_wave += 1
            progress.current_event_index = 0
            
            if progress.current_wave > len(waves):
                progress.is_completed = True
                return None
            
            wave = waves[progress.current_wave - 1]
        
        event = wave.events[progress.current_event_index]
        progress.current_event_index += 1
        
        return event
    
    @staticmethod
    def get_adventure_summary(progress: AdventureProgress, waves: List[AdventureWave]) -> str:
        """获取历练总结"""
        total_events = sum(len(w.events) for w in waves)
        
        summary = [
            f"\n{'='*50}",
            "              历 练 总 结",
            f"{'='*50}",
            f"副本类型: {progress.adventure_id}",
            f"完成波次: {progress.current_wave}/{len(waves)}",
            f"击败敌人: {progress.enemies_defeated}",
            f"造成伤害: {progress.total_damage_dealt:.0f}",
            f"受到伤害: {progress.total_damage_taken:.0f}",
        ]
        
        if progress.is_completed:
            summary.append("\n★★★ 历练完成! ★★★")
        elif progress.is_failed:
            summary.append("\n✗ 历练失败 ✗")
        else:
            summary.append(f"\n当前进度: {progress.current_event_index}/{len(waves[progress.current_wave-1].events) if progress.current_wave <= len(waves) else 0}")
        
        summary.append("="*50)
        
        return "\n".join(summary)


# ============ 便捷函数 ============

def start_dungeon(player: Player, difficulty: float = 1.0):
    """开始副本历练"""
    return AdventureSystem.start_adventure(player, AdventureType.DUNGEON, difficulty)


def start_trial(player: Player, difficulty: float = 1.0):
    """开始试炼"""
    return AdventureSystem.start_adventure(player, AdventureType.TRIAL, difficulty)


def start_secret_realm(player: Player, difficulty: float = 1.0):
    """开始秘境探索"""
    return AdventureSystem.start_adventure(player, AdventureType.SECRET_REALM, difficulty)


def start_boss_raid(player: Player, difficulty: float = 1.0):
    """开始Boss讨伐"""
    return AdventureSystem.start_adventure(player, AdventureType.BOSS_RAID, difficulty)
