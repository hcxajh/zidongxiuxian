"""
修仙游戏核心框架 - 渡劫系统
"""

import random
from typing import Optional, List
from dataclasses import dataclass
from enum import Enum
from core.player import Player, Realm


class TribulationType(Enum):
    """天劫类型"""
    SMALL = "小劫"      # 炼气->筑基
    MEDIUM = "中劫"     # 筑基->金丹
    LARGE = "大劫"      # 金丹->元婴
    HEAVENLY = "天劫"  # 元婴->化神


@dataclass
class Tribulation:
    """天劫配置"""
    type: TribulationType
    name: str
    thunder_count: int        # 天雷数量
    base_damage: float        # 基础伤害
    success_rate: float       # 基础成功率
    failure_penalty: float     # 失败惩罚比例 (扣除灵气比例)
    
    # 渡过后的奖励
    bonus_attack: int = 0
    bonus_defense: int = 0
    bonus_max_qi: float = 0.0


# 天劫配置表
TRIBULATION_CONFIG = {
    Realm.QI_REFINING: Tribulation(
        type=TribulationType.SMALL,
        name="炼气化神劫",
        thunder_count=3,
        base_damage=50,
        success_rate=0.8,
        failure_penalty=0.5,
        bonus_attack=5,
        bonus_defense=3,
        bonus_max_qi=50
    ),
    Realm.FOUNDATION: Tribulation(
        type=TribulationType.MEDIUM,
        name="筑基结丹劫",
        thunder_count=5,
        base_damage=150,
        success_rate=0.7,
        failure_penalty=0.6,
        bonus_attack=10,
        bonus_defense=5,
        bonus_max_qi=100
    ),
    Realm.GOLDEN_CORE: Tribulation(
        type=TribulationType.LARGE,
        name="金丹化婴劫",
        thunder_count=7,
        base_damage=300,
        success_rate=0.6,
        failure_penalty=0.7,
        bonus_attack=15,
        bonus_defense=8,
        bonus_max_qi=200
    ),
    Realm.NASENT_SOUL: Tribulation(
        type=TribulationType.HEAVENLY,
        name="元婴化神劫",
        thunder_count=9,
        base_damage=500,
        success_rate=0.5,
        failure_penalty=0.8,
        bonus_attack=20,
        bonus_defense=10,
        bonus_max_qi=300
    ),
}


# 渡劫辅助道具
class TribulationHelper:
    """渡劫辅助道具/阵法"""
    
    PROTECTION_ITEMS = {
        "shield_talisman": {
            "name": "护盾符",
            "description": "可抵挡一道天雷",
            "cost": 100,
            "thunder_absorption": 1
        },
        "defense_array": {
            "name": "防御阵法",
            "description": "降低天雷伤害30%",
            "cost": 200,
            "damage_reduction": 0.3
        },
        "qi_orb": {
            "name": "灵气珠",
            "description": "补充灵气",
            "cost": 50,
            "qi_restore": 100
        },
        "heaven_pill": {
            "name": "渡劫丹",
            "description": "提升渡劫成功率10%",
            "cost": 300,
            "success_rate_bonus": 0.1
        }
    }
    
    @staticmethod
    def get_available_helpers() -> List[dict]:
        """获取可用的辅助道具"""
        return list(TribulationHelper.PROTECTION_ITEMS.values())


class TribulationSystem:
    """渡劫系统"""
    
    @staticmethod
    def can_face_tribulation(player: Player) -> bool:
        """检查是否可以渡劫"""
        # 必须达到当前境界最大层数才能渡劫
        if player.level < player.realm.level_cap:
            return False
        # 灵气必须足够
        if player.qi < player.max_qi * 0.8:
            return False
        return True
    
    @staticmethod
    def get_tribulation_config(player: Player) -> Optional[Tribulation]:
        """获取当前境界的渡劫配置"""
        return TRIBULATION_CONFIG.get(player.realm)
    
    @staticmethod
    def calculate_success_rate(player: Player) -> float:
        """计算渡劫成功率"""
        tribulation = TribulationSystem.get_tribulation_config(player)
        if not tribulation:
            return 0.0
        
        # 基础成功率
        success_rate = tribulation.success_rate
        
        # 灵根加成 (变异灵根有额外加成)
        for element in player.elements:
            if element.value in ["雷", "风", "冰"]:
                success_rate += 0.05
        
        # 装备加成 (如果有防具)
        if player.armor:
            success_rate += 0.05
        
        # 限制成功率范围
        return min(max(success_rate, 0.1), 0.95)
    
    @staticmethod
    def face_tribulation(player: Player, use_helpers: List[str] = None) -> dict:
        """
        渡天劫
        返回结果: {
            "success": bool,
            "log": List[str],  # 渡劫过程日志
            "damage_taken": float  # 承受的天雷伤害
        }
        """
        use_helpers = use_helpers or []
        
        if not TribulationSystem.can_face_tribulation(player):
            return {
                "success": False,
                "log": ["灵气不足或未达到渡劫要求"],
                "damage_taken": 0
            }
        
        tribulation = TribulationSystem.get_tribulation_config(player)
        success_rate = TribulationSystem.calculate_success_rate(player)
        
        log = []
        log.append(f"\n{'='*50}")
        log.append(f"   ★★★ {tribulation.name} ★★★")
        log.append(f"{'='*50}")
        log.append(f"天雷数量: {tribulation.thunder_count}道")
        log.append(f"成功率: {success_rate*100:.1f}%")
        log.append("")
        
        # 处理使用的道具
        helpers_used = {}
        for helper_id in use_helpers:
            if helper_id in TribulationHelper.PROTECTION_ITEMS:
                helper = TribulationHelper.PROTECTION_ITEMS[helper_id]
                # 扣除灵石
                if player.spirit_stones >= helper["cost"]:
                    player.spirit_stones -= helper["cost"]
                    helpers_used[helper_id] = helper
                    log.append(f"使用 {helper['name']}: {helper['description']}")
                else:
                    log.append(f"灵石不足，无法使用 {helper['name']}")
        
        # 渡劫过程
        damage_taken = 0
        thunder_absorption = sum(h.get("thunder_absorption", 0) for h in helpers_used.values())
        damage_reduction = sum(h.get("damage_reduction", 0) for h in helpers_used.values())
        
        for i in range(tribulation.thunder_count):
            # 被吸收的天雷
            if thunder_absorption > 0:
                thunder_absorption -= 1
                log.append(f"第{i+1}道天雷被护盾符吸收!")
                continue
            
            # 计算天雷伤害
            damage = tribulation.base_damage * random.uniform(0.8, 1.2)
            damage *= (1 - damage_reduction)
            
            # 玩家防御减免
            defense_reduction = player.defense * 0.5
            actual_damage = max(damage - defense_reduction, damage * 0.3)
            
            damage_taken += actual_damage
            log.append(f"第{i+1}道天雷: 伤害 {actual_damage:.1f}")
            
            # 检查是否失败
            if damage_taken > player.qi:
                break
        
        log.append("")
        
        # 判断渡劫结果
        if damage_taken <= player.qi:
            # 渡劫成功
            # 消耗灵气
            player.qi -= damage_taken
            
            # 境界提升
            realm_index = list(Realm).index(player.realm)
            if realm_index < len(Realm) - 1:
                new_realm = list(Realm)[realm_index + 1]
                
                # 应用奖励
                player.realm = new_realm
                player.level = 1
                player.max_qi = player.max_qi * 1.5 + tribulation.bonus_max_qi
                player.qi = player.max_qi * 0.5  # 渡劫后恢复一半灵气
                player.attack += tribulation.bonus_attack
                player.defense += tribulation.bonus_defense
                
                log.append(f"✓ 渡劫成功! 境界提升至 {new_realm.value}!")
                log.append(f"  攻击+{tribulation.bonus_attack} 防御+{tribulation.bonus_defense}")
                log.append(f"  最大灵气+{tribulation.bonus_max_qi:.0f}")
                
                return {
                    "success": True,
                    "log": log,
                    "damage_taken": damage_taken
                }
        else:
            # 渡劫失败
            penalty_qi = player.max_qi * tribulation.failure_penalty
            player.qi = max(0, player.qi - penalty_qi)
            
            log.append(f"✗ 渡劫失败! 灵气损失 {penalty_qi:.1f}")
            
            return {
                "success": False,
                "log": log,
                "damage_taken": damage_taken
            }
        
        return {
            "success": False,
            "log": log,
            "damage_taken": damage_taken
        }
    
    @staticmethod
    def get_tribulation_info(player: Player) -> str:
        """获取渡劫信息"""
        if player.level < player.realm.level_cap:
            return f"当前 {player.realm.value} 第{player.level}层，需达到第{player.realm.level_cap}层方可渡劫"
        
        tribulation = TribulationSystem.get_tribulation_config(player)
        if not tribulation:
            return "已达最高境界，无需渡劫"
        
        success_rate = TribulationSystem.calculate_success_rate(player)
        
        info = f"""
【渡劫信息】
境界: {player.realm.value} 第{player.level}层 (渡劫临界)
天劫: {tribulation.name}
天雷: {tribulation.thunder_count}道
基础成功率: {tribulation.success_rate*100:.0f}%
当前成功率: {success_rate*100:.1f}%
天雷伤害: {tribulation.base_damage:.0f}
失败惩罚: 损失{tribulation.failure_penalty*100:.0f}%最大灵气

渡劫后可获得:
  攻击+{tribulation.bonus_attack}
  防御+{tribulation.bonus_defense}
  最大灵气+{tribulation.bonus_max_qi:.0f}
"""
        return info
