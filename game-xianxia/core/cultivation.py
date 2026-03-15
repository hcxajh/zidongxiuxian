"""
修仙游戏 - 修炼系统
"""

from typing import Optional, List
from core.player import Player


class Cultivation:
    """修炼系统"""
    
    # 境界突破所需灵气倍率
    BREAKTHROUGH_MULTIPLIER = 10.0
    
    # 每小时修炼获得的修为基数
    CULTIVATION_PER_HOUR = 5.0
    
    @staticmethod
    def meditate(player: Player, hours: float = 1.0) -> float:
        """
        打坐修炼
        返回获得的灵气，同时增加修为
        """
        base_qi = 10.0 * player.cultivation_speed
        bonus = 0.0
        
        # 灵根加成
        if player.elements:
            try:
                from core.element import ElementSystem
                synergy = ElementSystem.calculate_element_synergy(player.elements)
                bonus = synergy.get("cultivation", 1.0) - 1.0
            except ImportError:
                bonus = len(player.elements) * 0.2
        
        gained = (base_qi * (1 + bonus)) * hours
        overflow = player.gain_qi(gained)
        
        # 增加修为
        cultivation_gain = Cultivation.CULTIVATION_PER_HOUR * hours * player.cultivation_speed
        player.gain_cultivation(cultivation_gain)
        
        return gained - overflow
    
    @staticmethod
    def breakthrough_meditate(player: Player) -> dict:
        """
        突破境界修炼
        返回修炼结果
        """
        if player.level < player.realm.level_cap:
            return {
                "success": False,
                "message": f"需要在当前境界达到第{player.realm.level_cap}层才能突破"
            }
        
        if not player.can_breakthrough():
            return {
                "success": False,
                "message": "灵气不足，需要先将灵气修炼到上限"
            }
        
        cost = player.realm.breakthrough_cost
        if player.spirit_stones < cost:
            return {
                "success": False,
                "message": f"灵石不足，需要{cost}灵石进行突破"
            }
        
        # 执行突破
        old_realm = player.realm.value
        success = player.breakthrough()
        
        if success:
            return {
                "success": True,
                "message": f"突破成功！从{old_realm}晋升为{player.realm.value}！"
            }
        else:
            return {
                "success": False,
                "message": "突破失败"
            }
    
    @staticmethod
    def train_skill(player: Player, skill_id: str, hours: float = 1.0) -> dict:
        """
        功法修炼
        返回修炼结果
        """
        if skill_id not in player.skills:
            return {"success": False, "message": "未学会此功法"}
        
        player_skill = player.skills[skill_id]
        
        try:
            from core.skill import SKILLS_DATABASE
            skill = SKILLS_DATABASE.get(skill_id)
            
            if not skill:
                return {"success": False, "message": "功法不存在"}
            
            if player_skill.is_max_level:
                return {"success": False, "message": "功法已满级"}
            
            # 计算获得的经验
            # 消耗灵气来修炼
            qi_cost = 20.0 * hours
            if not player.consume_qi(qi_cost):
                return {"success": False, "message": "灵气不足"}
            
            exp_gained = hours * 10.0
            leveled_up = player_skill.add_exp(exp_gained)
            
            result = {
                "success": True,
                "exp_gained": exp_gained,
                "current_exp": player_skill.exp,
                "exp_needed": player_skill.exp_needed,
                "message": f"修炼【{skill.name}】获得{exp_gained}熟练度"
            }
            
            if leveled_up:
                result["message"] += f"，升级到第{player_skill.level}层！"
                result["leveled_up"] = True
                result["new_level"] = player_skill.level
            
            return result
            
        except ImportError:
            return {"success": False, "message": "技能系统未加载"}
    
    @staticmethod
    def realm_meditation(player: Player, realm_name: str) -> dict:
        """
        境界共鸣修炼
        与对应境界的灵气产生共鸣
        """
        realm_bonus = {
            "炼气期": 1.2,
            "筑基期": 1.5,
            "金丹期": 2.0,
            "元婴期": 3.0,
            "化神期": 5.0,
        }
        
        bonus = realm_bonus.get(realm_name, 1.0)
        base_qi = 10.0 * player.cultivation_speed * bonus
        gained = base_qi
        overflow = player.gain_qi(gained)
        
        return {
            "success": True,
            "message": f"进行{realm_name}共鸣修炼，获得{gained-overflow:.1f}点灵气",
            "qi_gained": gained - overflow
        }
    
    @staticmethod
    def consume_resource(player: Player, resource: str, amount: int) -> bool:
        """消耗资源"""
        costs = {
            "spirit_stone": ("spirit_stones", amount),
        }
        
        if resource == "spirit_stone":
            if player.spirit_stones >= amount:
                player.spirit_stones -= amount
                return True
        return False
    
    @staticmethod
    def get_cultivation_progress(player: Player) -> dict:
        """获取修炼进度"""
        qi_percent = player.qi / player.max_qi * 100
        
        # 检查是否可以突破
        can_break = player.can_breakthrough()
        breakthrough_cost = player.realm.breakthrough_cost
        
        progress = {
            "realm": player.realm.value,
            "level": player.level,
            "level_cap": player.realm.level_cap,
            "qi": player.qi,
            "max_qi": player.max_qi,
            "qi_percent": qi_percent,
            "cultivation_speed": player.cultivation_speed,
            "can_breakthrough": can_break,
            "breakthrough_cost": breakthrough_cost,
        }
        
        return progress
