"""
修仙游戏 - 世界/地图/副本系统
"""

import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from core.player import Player, Realm
from core.combat import Combat
from data.maps import (
    MAP_NODES, DUNGEONS, MapNode, Dungeon, 
    DungeonDifficulty, get_available_dungeons, get_available_map_nodes,
    MapRegionType
)


# 玩家通关记录
player_dungeon_records: Dict[str, Dict] = {}


class World:
    """世界系统"""
    
    @staticmethod
    def show_map(player: Player):
        """显示当前境界可访问的地图"""
        print("\n" + "=" * 60)
        print(f"       【{player.realm.value}】地图")
        print("=" * 60)
        
        nodes = get_available_map_nodes(player.realm)
        
        # 按区域类型分组
        cities = [n for n in nodes if n.region_type == MapRegionType.CITY]
        wilds = [n for n in nodes if n.region_type == MapRegionType.WILDERNESS]
        caves = [n for n in nodes if n.region_type == MapRegionType.CAVE]
        secrets = [n for n in nodes if n.region_type == MapRegionType.SECRET]
        
        print("\n【城池】(安全区)")
        for node in cities:
            print(f"  • {node.name}: {node.description}")
        
        print("\n【野外】(历练区)")
        for node in wilds:
            print(f"  • {node.name}: {node.description}")
        
        print("\n【洞府】(副本入口)")
        for node in caves:
            print(f"  • {node.name}: {node.description}")
        
        if secrets:
            print("\n【秘境】(隐藏区域)")
            for node in secrets:
                print(f"  • {node.name}: {node.description}")
        
        print("\n" + "-" * 60)
    
    @staticmethod
    def explore(player: Player, node_id: str) -> str:
        """探索地图节点"""
        node = MAP_NODES.get(node_id)
        if not node:
            return f"未找到地图节点: {node_id}"
        
        # 检查境界要求
        if list(Realm).index(player.realm) < list(Realm).index(node.min_realm):
            return f"境界不足，需要 {node.min_realm.value} 才能进入"
        
        # 无敌人直接返回
        if not node.enemies:
            return f"\n你来到了【{node.name}】\n{node.description}\n\n此处安全，无危险。"
        
        # 遭遇敌人
        enemy = Combat.create_enemy(player.realm, player.level)
        print(f"\n你来到了【{node.name}】")
        print(f"突然，一只{enemy.name}窜了出来!")
        
        input("\n按回车开始战斗...")
        
        win, log = Combat.battle(player, enemy)
        print(log)
        
        if win:
            # 战斗胜利奖励
            spirit_stones = random.randint(5, 20) * player.level
            qi_reward = random.randint(10, 30) * player.level
            
            player.spirit_stones += spirit_stones
            overflow = player.gain_qi(qi_reward)
            
            return f"""
战斗胜利!
获得: 灵石 {spirit_stones}, 灵气 {qi_reward}
"""
        else:
            return "\n战斗失败，疗伤后返回..."
    
    @staticmethod
    def list_dungeons(player: Player) -> List[Dict]:
        """列出可进入的副本"""
        return get_available_dungeons(player.realm)
    
    @staticmethod
    def enter_dungeon(player: Player, dungeon_id: str) -> str:
        """进入副本"""
        dungeon = DUNGEONS.get(dungeon_id)
        if not dungeon:
            return f"未找到副本: {dungeon_id}"
        
        # 检查境界要求
        if list(Realm).index(player.realm) < list(Realm).index(dungeon.min_realm):
            return f"境界不足，需要 {dungeon.min_realm.value} 才能进入副本"
        
        # 获取玩家记录
        player_id = id(player)
        if player_id not in player_dungeon_records:
            player_dungeon_records[player_id] = {}
        
        records = player_dungeon_records[player_id]
        is_first_clear = dungeon.id not in records
        
        print("\n" + "=" * 60)
        print(f"       进入副本: {dungeon.name}")
        print(f"       难度: {dungeon.difficulty.value}")
        print("=" * 60)
        print(f"\n{dungeon.description}")
        
        if is_first_clear:
            print("\n★ 首次通关奖励丰厚! ★")
        
        input("\n按回车开始挑战...")
        
        # 生成敌人波次
        all_enemies = []
        for wave in dungeon.enemies:
            for _ in range(wave["count"]):
                level = random.randint(wave["level_range"][0], wave["level_range"][1])
                enemy = Combat.create_enemy(wave["realm"], level)
                all_enemies.append(enemy)
        
        total_enemies = len(all_enemies)
        defeated = 0
        
        print(f"\n副本中共有 {total_enemies} 个敌人!\n")
        
        for i, enemy in enumerate(all_enemies, 1):
            print(f"\n--- 第 {i}/{total_enemies} 波 ---")
            print(f"敌人: {enemy.name}")
            print(f"HP: {enemy.hp:.1f} | 攻击: {enemy.attack} | 防御: {enemy.defense}")
            
            input("按回车继续...")
            
            win, log = Combat.battle(player, enemy)
            print(log)
            
            if not win:
                return "\n\n★★★ 副本失败! 你被打败了 ★★★\n只能狼狈退出..."
            
            defeated += 1
        
        # 副本通关!
        print("\n" + "=" * 60)
        print(f"       ★★★ {dungeon.name} 通关! ★★★")
        print("=" * 60)
        
        # 记录通关
        records[dungeon.id] = True
        
        # 计算奖励
        result = []
        
        # 基础奖励
        ss_min, ss_max = dungeon.rewards.get("spirit_stones", (0, 0))
        if ss_min > 0:
            ss_reward = random.randint(ss_min, ss_max)
            player.spirit_stones += ss_reward
            result.append(f"灵石: +{ss_reward}")
        
        qi_min, qi_max = dungeon.rewards.get("qi", (0, 0))
        if qi_min > 0:
            qi_reward = random.randint(qi_min, qi_max)
            player.gain_qi(qi_reward)
            result.append(f"灵气: +{qi_reward}")
        
        # 物品奖励
        items = dungeon.rewards.get("items", [])
        if items:
            item = random.choice(items)
            # TODO: 添加物品到玩家背包
            result.append(f"物品: {item}")
        
        # 首次通关额外奖励
        if is_first_clear:
            print("\n【首次通关奖励】")
            first_ss = dungeon.first_clear_reward.get("spirit_stones", 0)
            if first_ss:
                player.spirit_stones += first_ss
                print(f"  灵石: +{first_ss}")
            
            first_items = dungeon.first_clear_reward.get("items", [])
            for item in first_items:
                print(f"  物品: {item}")
                result.append(f"[首通] {item}")
        
        return f"\n{' | '.join(result)}\n\n恭喜完成副本挑战!"


class DungeonManager:
    """副本管理器"""
    
    @staticmethod
    def get_dungeon_info(dungeon_id: str) -> Optional[Dungeon]:
        """获取副本信息"""
        return DUNGEONS.get(dungeon_id)
    
    @staticmethod
    def is_first_clear(player: Player, dungeon_id: str) -> bool:
        """检查是否首次通关"""
        player_id = id(player)
        records = player_dungeon_records.get(player_id, {})
        return dungeon_id not in records
    
    @staticmethod
    def get_clear_count(player: Player, dungeon_id: str) -> int:
        """获取通关次数"""
        # 简化实现，返回是否通关的布尔值
        player_id = id(player)
        records = player_dungeon_records.get(player_id, {})
        return 1 if dungeon_id in records else 0
