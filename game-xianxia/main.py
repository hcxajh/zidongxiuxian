#!/usr/bin/env python3
"""
修仙游戏 - 核心框架入口
"""

from core.player import Player, Realm, create_player, REALM_SUPPRESSION
from core.cultivation import Cultivation
from core.skill import SkillSystem, SKILLS_DATABASE, SkillType
from core.element import Element, ElementType, ElementSystem
from core.tribulation import TribulationSystem, TribulationHelper
from core.disciple import DiscipleSystem, Disciple, DiscipleState
from core.beast import BeastSystem, Beast, BeastState, BeastQuality
from core.sect import SectSystem, Sect, SectBuilding, SectRank, BUILDING_CONFIG, SectTaskType
from core.partner import PartnerSystem, Partner, PartnerState, PARTNER_GIFTS
from core.adventure import AdventureSystem, AdventureType, AdventureEventType
from core.database import save_player, load_player, list_saved_players, delete_player
import random


def load_or_create_player():
    """加载已有角色或创建新角色"""
    saved_players = list_saved_players()
    
    if not saved_players:
        print("\n【新游戏】尚未有任何存档，将创建新角色")
        return create_character()
    
    # 显示已有存档
    print("\n" + "=" * 50)
    print("       仙 途 - 游 戏 菜 单")
    print("=" * 50)
    print("\n【已有存档】")
    for i, p in enumerate(saved_players, 1):
        print(f"{i}. {p['name']} - {p['realm']}第{p['level']}层")
        print(f"   灵石: {p['spirit_stones']} | 修为: {p['cultivation']:.0f}")
        print(f"   上次更新: {p['updated_at'][:19] if p['updated_at'] else '未知'}")
    
    print(f"\n{len(saved_players) + 1}. 创建新角色")
    print("0. 退出游戏")
    
    choice = input("\n请选择: ").strip()
    
    if choice == "0":
        print("\n后会有期!")
        exit(0)
    
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(saved_players):
            # 加载已有存档
            player_name = saved_players[idx]['name']
            player = load_player(player_name)
            if player:
                print(f"\n★★★ 欢迎回来，{player.name}! ★★★")
                return player
            else:
                print("\n加载存档失败，将创建新角色")
                return create_character()
        elif idx == len(saved_players):
            # 创建新角色
            return create_character()
    
    print("\n无效选择，将创建新角色")
    return create_character()


def create_character():
    """创建角色"""
    print("=" * 50)
    print("       仙 途 - 创 建 角 色")
    print("=" * 50)
    
    name = input("请输入角色名称: ").strip() or "无名修士"
    
    print("\n选择灵根生成方式:")
    print("1. 随机生成灵根")
    print("2. 指定天灵根")
    
    choice = input("选择 (1/2): ").strip()
    
    elements = []
    if choice == "2":
        # 选择想要的灵根类型
        print("\n选择灵根元素:")
        all_elements = list(ElementType)
        for i, e in enumerate(all_elements, 1):
            print(f"  {i}. {e.value}")
        
        e_choice = input("选择: ").strip()
        if e_choice.isdigit() and 1 <= int(e_choice) <= len(all_elements):
            selected_type = all_elements[int(e_choice) - 1]
            grade = 10  # 天灵根
            elements = [Element(type=selected_type, grade=grade)]
    else:
        # 随机生成灵根
        num = input("灵根数量 (1-3，默认2): ").strip()
        num = int(num) if num.isdigit() and 1 <= int(num) <= 3 else 2
        elements = ElementSystem.generate_player_elements(num, grade_range=(5, 9))
    
    player = create_player(name, elements)
    
    # 赠送初始功法
    from core.skill import PlayerSkill
    player.skills["intro_cultivation"] = PlayerSkill("intro_cultivation", 1)
    player.cultivation_speed = SkillSystem.get_cultivation_bonus(player)
    
    print(f"\n{'='*40}")
    print("角色创建成功!")
    print(f"境界: {player.realm.value}")
    print(f"灵根: {', '.join([e.name for e in player.elements])}")
    print(f"修炼速度: {player.cultivation_speed:.2f}x")
    print(f"{'='*40}")
    
    return player


def main_menu(player: Player):
    """主菜单"""
    while True:
        print("\n" + "=" * 50)
        print(f"       仙 途 - {player.name}")
        print("=" * 50)
        print(player.status())
        
        print("\n【行动】")
        print("1. 打坐修炼")
        print("2. 境界突破")
        print("3. 境界升级 (消耗修为)")
        print("4. 渡天劫 (需第10层)")
        print("5. 战斗历练")
        print("6. 历练副本")
        print("7. 学习功法")
        print("8. 查看功法")
        print("9. 升级功法")
        print("A. 战斗(使用功法)")
        print("B. 装备系统")
        print("C. 弟子管理系统")
        print("D. 灵兽伙伴系统")
        print("E. 宗门系统")
        print("F. 仙侣道侣系统")
        print("S. 保存游戏")
        print("G. 删除角色")
        print("0. 退出游戏")
        
        choice = input("\n请选择: ").strip()
        
        if choice == "1":
            do_meditate(player)
        elif choice == "2":
            do_breakthrough(player)
        elif choice == "3":
            do_level_up(player)
        elif choice == "4":
            do_tribulation(player)
        elif choice == "5":
            do_combat(player)
        elif choice == "6":
            adventure_menu(player)
        elif choice == "7":
            learn_skill(player)
        elif choice == "8":
            list_skills(player)
        elif choice == "9":
            upgrade_skill(player)
        elif choice.lower() == "a":
            combat_with_skills(player)
        elif choice.lower() == "b":
            equipment_menu(player)
        elif choice.lower() == "c":
            disciple_menu(player)
        elif choice.lower() == "d":
            beast_menu(player)
        elif choice.lower() == "e":
            sect_menu(player)
        elif choice.lower() == "f":
            partner_menu(player)
        elif choice.lower() == "s":
            # 保存游戏
            if save_player(player):
                print("\n★★★ 游戏已自动保存 ★★★")
            else:
                print("\n✗ 保存失败")
        elif choice.lower() == "g":
            # 删除角色（需要确认）
            confirm = input("\n确定要删除角色 【{}】 吗？此操作不可恢复！(y/n): ".format(player.name)).strip().lower()
            if confirm == "y":
                if delete_player(player.name):
                    print("\n角色已删除")
                    return  # 退出主菜单
                else:
                    print("\n删除失败")
        elif choice == "0":
            print("\n后会有期!")
            break


def do_meditate(player: Player):
    """打坐修炼"""
    hours = input("修炼时长 (小时): ").strip()
    hours = float(hours) if hours.replace(".", "").isdigit() else 1.0
    
    gained = Cultivation.meditate(player, hours)
    print(f"\n修炼 {hours} 小时，获得灵气: {gained:.1f}")
    print(f"当前灵气: {player.qi:.1f}/{player.max_qi:.1f}")
    
    # 检查是否可突破
    if player.level >= player.realm.level_cap and player.qi >= player.max_qi:
        print(">>> 灵气已满，达到当前境界巅峰，可以突破! <<<")


def do_breakthrough(player: Player):
    """境界突破"""
    if player.level < player.realm.level_cap:
        print(f"\n需要在当前境界达到第{player.realm.level_cap}层才能突破")
        print(f"当前: 第{player.level}层")
        return
    
    if player.qi < player.max_qi:
        print(f"\n灵气不足 ({player.qi:.1f}/{player.max_qi})，无法突破")
        return
    
    cost = player.realm.breakthrough_cost
    if player.spirit_stones < cost:
        print(f"\n灵石不足，需要{cost}灵石")
        return
    
    result = Cultivation.breakthrough_meditate(player)
    print(f"\n{result['message']}")


def do_level_up(player: Player):
    """境界层数升级"""
    if player.level >= player.realm.level_cap:
        print(f"\n已达当前境界最高层(第{player.realm.level_cap}层)，需渡天劫突破到下一境界")
        print(TribulationSystem.get_tribulation_info(player))
        return
    
    if not player.can_level_up():
        required = player.get_level_up_requirement()
        print(f"\n修为不足!")
        print(f"当前: {player.cultivation:.1f} / 需要: {required:.0f}")
        print("请继续打坐修炼积累修为")
        return
    
    if player.level_up():
        print(f"\n★★★ 升级成功! {player.realm.value} 第{player.level}层 ★★★")
        print(f"最大灵气: {player.max_qi:.1f}, 攻击: {player.attack}, 防御: {player.defense}")
    else:
        print("\n升级失败")


def do_tribulation(player: Player):
    """渡天劫"""
    if player.level < player.realm.level_cap:
        print(f"\n当前 {player.realm.value} 第{player.level}层，需达到第{player.realm.level_cap}层方可渡劫")
        return
    
    print(TribulationSystem.get_tribulation_info(player))
    
    # 检查是否可以渡劫
    if not TribulationSystem.can_face_tribulation(player):
        print("\n当前状态无法渡劫:")
        print(f"  灵气: {player.qi:.1f}/{player.max_qi:.1f} (需要80%以上)")
        print("请先打坐修炼恢复灵气")
        return
    
    # 询问是否使用道具
    print("\n【渡劫辅助商店】")
    helpers = TribulationHelper.get_available_helpers()
    for i, h in enumerate(helpers, 1):
        print(f"  {i}. {h['name']} - {h['description']} (灵石: {h['cost']})")
    print("  0. 不使用道具，直接渡劫")
    
    choice = input("\n选择道具 (可多选，用逗号分隔): ").strip()
    selected_helpers = []
    
    if choice.strip():
        indices = [int(x.strip()) - 1 for x in choice.split(",") if x.strip().isdigit()]
        for idx in indices:
            if 0 <= idx < len(helpers):
                helper_key = list(TribulationHelper.PROTECTION_ITEMS.keys())[idx]
                selected_helpers.append(helper_key)
    
    # 开始渡劫
    result = TribulationSystem.face_tribulation(player, selected_helpers)
    
    for log_line in result["log"]:
        print(log_line)


def do_combat(player: Player):
    """战斗"""
    # 简单战斗
    import random
    
    enemy_hp = 50 + player.level * 10
    enemy_attack = 5 + player.level * 2
    
    print(f"\n遭遇敌人! HP: {enemy_hp}, 攻击: {enemy_attack}")
    
    while player.hp > 0 and enemy_hp > 0:
        # 玩家攻击
        damage = player.attack
        if random.random() < player.crit:
            damage = int(damage * 1.5)
            print(f"暴击! ", end="")
        enemy_hp -= damage
        print(f"你对敌人造成 {damage} 点伤害")
        
        if enemy_hp <= 0:
            break
        
        # 敌人攻击
        actual = player.take_damage(enemy_attack)
        print(f"敌人对你造成 {actual} 点伤害")
    
    if player.hp > 0:
        reward = player.level * 10 + 20
        player.spirit_stones += reward
        print(f"\n★★★ 战斗胜利! 获得{reward}灵石 ★★★")
        player.hp = player.max_hp  # 战后恢复
    else:
        print("\n💀 战斗失败... 💀")


def adventure_menu(player: Player):
    """历练副本菜单"""
    while True:
        print("\n" + "=" * 50)
        print("       历 练 副 本")
        print("=" * 50)
        print(f"境界: {player.realm.value} 第{player.level}层")
        print(f"灵气: {player.qi:.1f}/{player.max_qi:.1f}")
        print(f"灵石: {player.spirit_stones}")
        
        print("\n【历练类型】")
        print("1. 副本挑战 (5波次，含Boss)")
        print("2. 试炼塔 (10波次，越往后越难)")
        print("3. 秘境探索 (7波次，奖励丰富)")
        print("4. Boss讨伐 (单挑强大Boss)")
        print("0. 返回主菜单")
        
        choice = input("\n请选择: ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            start_adventure_by_type(player, AdventureType.DUNGEON)
        elif choice == "2":
            start_adventure_by_type(player, AdventureType.TRIAL)
        elif choice == "3":
            start_adventure_by_type(player, AdventureType.SECRET_REALM)
        elif choice == "4":
            start_adventure_by_type(player, AdventureType.BOSS_RAID)
        else:
            print("无效选择")


def start_adventure_by_type(player: Player, adventure_type: AdventureType):
    """根据类型开始历练"""
    # 选择难度
    print("\n【选择难度】")
    print("1. 简单 (1.0x)")
    print("2. 普通 (1.5x)")
    print("3. 困难 (2.0x)")
    print("4. 噩梦 (3.0x)")
    
    diff_choice = input("选择难度: ").strip()
    difficulty_map = {"1": 1.0, "2": 1.5, "3": 2.0, "4": 3.0}
    difficulty = difficulty_map.get(diff_choice, 1.0)
    
    # 检查灵气是否足够
    min_qi_required = player.max_qi * 0.5
    if player.qi < min_qi_required:
        print(f"\n灵气不足! 需要至少 {min_qi_required:.1f} 灵气才能开始历练")
        print(f"当前灵气: {player.qi:.1f}")
        return
    
    # 开始历练
    print(f"\n开始{adventure_type.value}...")
    waves, progress = AdventureSystem.start_adventure(player, adventure_type, difficulty)
    
    # 历练主循环
    while not progress.is_completed and not progress.is_failed and player.qi > 0:
        # 获取当前事件
        event = AdventureSystem.advance_event(waves, progress)
        
        if event is None:
            break
        
        # 显示事件信息
        print(f"\n{'='*50}")
        print(f"第{progress.current_wave}波 - {event.event_type.value}: {event.name}")
        print(f"{event.description}")
        print(f"{'='*50}")
        
        # 处理事件
        result = AdventureSystem.process_event(player, event, waves, progress)
        
        # 显示结果
        if "log" in result:
            print(result["log"])
        
        # 检查是否失败
        if player.qi <= 0:
            progress.is_failed = True
            print("\n💀 灵气耗尽，历练失败! 💀")
            break
        
        # 询问是否继续
        if not progress.is_completed and not progress.is_failed:
            print(f"\n当前状态: 灵气 {player.qi:.1f}/{player.max_qi:.1f}")
            cont = input("继续下一事件? (y/n): ").strip().lower()
            if cont != "y" and cont != "是":
                print("选择退出历练")
                break
    
    # 显示总结
    summary = AdventureSystem.get_adventure_summary(progress, waves)
    print(summary)
    
    # 发放奖励
    if progress.is_completed and not progress.is_failed:
        rewards = AdventureSystem.calculate_rewards(waves, progress, player)
        print(f"\n【历练奖励】")
        print(f"  灵石: +{rewards['spirit_stones']}")
        print(f"  修为: +{rewards['cultivation']}")
        player.spirit_stones += rewards['spirit_stones']
        player.cultivation += rewards['cultivation']
        
        # 保存首通记录（这里可以用简单的玩家属性存储）
        if not hasattr(player, 'adventure_records'):
            player.adventure_records = {}
        
        record_key = f"{adventure_type.value}_{difficulty}"
        if record_key not in player.adventure_records:
            player.adventure_records[record_key] = True
            print("\n★ 首次通关奖励! ★")


def learn_skill(player: Player):
    """学习功法"""
    available = SkillSystem.get_available_skills(player)
    
    if not available:
        print("\n暂无可学习的功法")
        return
    
    print("\n【可学习功法】")
    for i, skill in enumerate(available, 1):
        cost = skill.grade.stars * 50
        print(f"{i}. {skill.name} ({skill.grade.name})")
        print(f"   消耗: {cost}灵石 | 元素: {skill.element.value}")
        print(f"   {skill.description}")
        if skill.effects:
            print(f"   效果: {skill.effects[0].description}")
        print()
    
    choice = input("选择功法 (序号): ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(available):
        skill = available[int(choice) - 1]
        success, msg = SkillSystem.learn_skill(player, skill.id)
        print(f"\n{msg}")
        if success:
            # 更新玩家属性
            player.cultivation_speed = SkillSystem.get_cultivation_bonus(player)


def list_skills(player: Player):
    """查看已学功法"""
    if not player.skills:
        print("\n尚未学习任何功法")
        return
    
    print("\n【已学功法】")
    for skill_id, ps in player.skills.items():
        skill = SKILLS_DATABASE.get(skill_id)
        if skill:
            print(f"  • {skill.name} (等级{ps.level})")
            if skill.effects:
                print(f"    {skill.effects[0].description}")
            if ps.exp_needed > 0:
                print(f"    熟练度: {ps.exp:.0f}/{ps.exp_needed}")


def upgrade_skill(player: Player):
    """升级功法"""
    if not player.skills:
        print("\n尚未学习任何功法")
        return
    
    print("\n【升级功法】")
    for skill_id, ps in player.skills.items():
        skill = SKILLS_DATABASE.get(skill_id)
        if skill:
            exp_needed = ps.exp_needed
            status = f"熟练度: {ps.exp:.0f}/{exp_needed}" if exp_needed > 0 else "已满级"
            print(f"  {skill.name}: {status}")
    
    skill_name = input("\n输入要升级的功法名称: ").strip()
    for skill_id in player.skills:
        skill = SKILLS_DATABASE.get(skill_id)
        if skill and skill.name == skill_name:
            result = Cultivation.train_skill(player, skill_id, 1.0)
            print(f"\n{result.get('message', result.get('message', '失败'))}")
            return
    
    print("未找到该功法")


def combat_with_skills(player: Player):
    """使用功法的战斗"""
    if not player.skills:
        print("\n尚未学习任何功法")
        return
    
    # 显示可用攻击功法
    attack_skills = []
    for skill_id in player.skills:
        skill = SKILLS_DATABASE.get(skill_id)
        if skill and skill.type in [SkillType.ATTACK, SkillType.DEFENSE]:
            attack_skills.append((skill_id, skill))
    
    if not attack_skills:
        print("\n没有攻击或防御功法")
        return
    
    print("\n【选择功法】")
    for i, (skill_id, skill) in enumerate(attack_skills, 1):
        print(f"{i}. {skill.name} (消耗{skill.qi_cost}灵气)")
    
    choice = input("选择: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(attack_skills):
        skill_id, skill = attack_skills[int(choice) - 1]
        
        # 模拟敌人
        enemy_hp = 100
        enemy_attack = 15
        
        print(f"\n使用【{skill.name}】!")
        result = SkillSystem.use_skill(skill_id, player)
        
        if result["success"]:
            if result.get("damage"):
                enemy_hp -= result["damage"]
                print(f"对敌人造成 {result['damage']} 点伤害!")
            if result.get("defense"):
                print(f"获得 {result['defense']} 点防御加成!")
            
            if enemy_hp <= 0:
                reward = player.level * 20 + 50
                player.spirit_stones += reward
                print(f"\n★★★ 战斗胜利! 获得{reward}灵石 ★★★")
            else:
                actual = player.take_damage(enemy_attack)
                print(f"敌人反击! 你受到 {actual} 点伤害")
        else:
            print(f"使用失败: {result['message']}")


# ========== 弟子系统功能 ==========

def disciple_menu(player: Player):
    """弟子管理菜单"""
    if not hasattr(player, 'disciples'):
        player.disciples = []
    
    while True:
        print("\n" + "=" * 40)
        print("       【弟子管理系统】")
        print("=" * 40)
        print(DiscipleSystem.get_disciple_summary(player.disciples))
        
        print("\n【行动】")
        print("1. 招收弟子")
        print("2. 查看弟子详情")
        print("3. 指导修炼")
        print("4. 派遣战斗")
        print("5. 驱逐弟子")
        print("0. 返回主菜单")
        
        choice = input("\n请选择: ").strip()
        
        if choice == "1":
            recruit_disciple(player)
        elif choice == "2":
            view_disciple(player)
        elif choice == "3":
            train_disciple(player)
        elif choice == "4":
            send_disciple_combat(player)
        elif choice == "5":
            dismiss_disciple(player)
        elif choice == "0":
            break


def recruit_disciple(player: Player):
    """招收弟子"""
    if len(player.disciples) >= 10:
        print("\n弟子数量已达上限(10人)")
        return
    
    print("\n【招收弟子】")
    cost = 50 * (len(player.disciples) + 1)
    print(f"消耗灵石: {cost}")
    
    if player.spirit_stones < cost:
        print("灵石不足!")
        return
    
    player.spirit_stones -= cost
    new_disciple = DiscipleSystem.recruit_disciple(player.disciples, player.realm.value)
    player.disciples.append(new_disciple)
    
    print(f"\n★★★ 成功招收弟子: {new_disciple.name} ★★★")
    print(new_disciple.status())


def view_disciple(player: Player):
    """查看弟子详情"""
    if not player.disciples:
        print("\n暂无弟子")
        return
    
    print("\n【选择弟子】")
    for i, d in enumerate(player.disciples, 1):
        print(f"{i}. {d.name} - {d.realm}第{d.level}层")
    
    choice = input("选择: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(player.disciples):
        disciple = player.disciples[int(choice) - 1]
        print(disciple.status())


def train_disciple(player: Player):
    """指导弟子修炼"""
    if not player.disciples:
        print("\n暂无弟子")
        return
    
    print("\n【选择弟子】")
    for i, d in enumerate(player.disciples, 1):
        print(f"{i}. {d.name}")
    
    choice = input("选择: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(player.disciples):
        disciple = player.disciples[int(choice) - 1]
        
        hours = input("修炼时长 (小时): ").strip()
        hours = float(hours) if hours.replace(".", "").isdigit() and float(hours) > 0 else 1.0
        
        result = DiscipleSystem.train_disciple(disciple, hours)
        
        print(f"\n修炼 {hours} 小时，{disciple.name} 获得修为: {result['cultivation_gain']:.1f}")
        print(f"当前修为: {result['new_cultivation']:.1f}")
        
        if result.get("leveled_up"):
            print(f"★★★ 升级到第{result['new_level']}层! ★★★")


def send_disciple_combat(player: Player):
    """派遣弟子战斗"""
    if not player.disciples:
        print("\n暂无弟子")
        return
    
    # 选择可战斗的弟子
    available = [d for d in player.disciples if d.hp > 0]
    if not available:
        print("\n没有可战斗的弟子")
        return
    
    print("\n【选择弟子】")
    for i, d in enumerate(available, 1):
        print(f"{i}. {d.name} (HP:{d.hp}/{d.max_hp})")
    
    choice = input("选择: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(available):
        disciple = available[int(choice) - 1]
        
        enemy_level = player.level
        result = DiscipleSystem.send_to_combat(disciple, enemy_level)
        
        print("\n【战斗开始】")
        for log in result["log"]:
            print(log)
        
        if result["win"]:
            print(f"\n★★★ 战斗胜利! 获得{result['merits']}战功 ★★★")
        else:
            print("\n💀 战斗失败... 💀")


def dismiss_disciple(player: Player):
    """驱逐弟子"""
    if not player.disciples:
        print("\n暂无弟子")
        return
    
    print("\n【选择弟子】")
    for i, d in enumerate(player.disciples, 1):
        print(f"{i}. {d.name}")
    
    choice = input("选择: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(player.disciples):
        disciple = player.disciples.pop(int(choice) - 1)
        print(f"\n{DiscipleSystem.dismiss_disciple(disciple)}")


# ========== 灵兽系统功能 ==========

def beast_menu(player: Player):
    """灵兽管理菜单"""
    if not hasattr(player, 'beasts'):
        player.beasts = []
    
    while True:
        print("\n" + "=" * 40)
        print("       【灵兽伙伴系统】")
        print("=" * 40)
        print(BeastSystem.get_beast_summary(player.beasts))
        
        print("\n【行动】")
        print("1. 契约灵兽")
        print("2. 查看灵兽详情")
        print("3. 训练灵兽")
        print("4. 派遣战斗")
        print("5. 联手战斗")
        print("6. 喂食灵兽")
        print("7. 灵兽进化")
        print("8. 放生灵兽")
        print("0. 返回主菜单")
        
        choice = input("\n请选择: ").strip()
        
        if choice == "1":
            contract_beast(player)
        elif choice == "2":
            view_beast(player)
        elif choice == "3":
            train_beast(player)
        elif choice == "4":
            send_beast_combat(player)
        elif choice == "5":
            combined_battle(player)
        elif choice == "6":
            feed_beast(player)
        elif choice == "7":
            evolution_beast(player)
        elif choice == "8":
            release_beast(player)
        elif choice == "0":
            break


def contract_beast(player: Player):
    """契约灵兽"""
    if len(player.beasts) >= 5:
        print("\n灵兽数量已达上限(5只)")
        return
    
    print("\n【契约灵兽】")
    cost = 100 * (len(player.beasts) + 1)
    print(f"消耗灵石: {cost}")
    
    if player.spirit_stones < cost:
        print("灵石不足!")
        return
    
    player.spirit_stones -= cost
    new_beast = BeastSystem.contract_beast(player.beasts, player.realm.value)
    player.beasts.append(new_beast)
    
    quality_color = new_beast.get_quality_color()
    print(f"\n★★★ 成功契约灵兽: {new_beast.name} ({quality_color}) ★★★")
    print(new_beast.status())


def view_beast(player: Player):
    """查看灵兽详情"""
    if not player.beasts:
        print("\n暂无灵兽")
        return
    
    print("\n【选择灵兽】")
    for i, b in enumerate(player.beasts, 1):
        print(f"{i}. {b.name} - {b.realm}第{b.level}层")
    
    choice = input("选择: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(player.beasts):
        beast = player.beasts[int(choice) - 1]
        print(beast.status())


def train_beast(player: Player):
    """训练灵兽"""
    if not player.beasts:
        print("\n暂无灵兽")
        return
    
    print("\n【选择灵兽】")
    for i, b in enumerate(player.beasts, 1):
        print(f"{i}. {b.name}")
    
    choice = input("选择: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(player.beasts):
        beast = player.beasts[int(choice) - 1]
        
        hours = input("训练时长 (小时): ").strip()
        hours = float(hours) if hours.replace(".", "").isdigit() and float(hours) > 0 else 1.0
        
        result = beast.train(hours)
        
        if "error" in result:
            print(f"\n{result['error']}")
        else:
            print(f"\n{result['message']}")
            if result.get("leveled_up"):
                print(f"★★★ 升级到第{result['new_level']}层! ★★★")
            if result.get("can_evolution"):
                print(f">>> 可以进化了! <<<")


def send_beast_combat(player: Player):
    """派遣灵兽战斗"""
    if not player.beasts:
        print("\n暂无灵兽")
        return
    
    available = [b for b in player.beasts if b.hp > 0]
    if not available:
        print("\n没有可战斗的灵兽")
        return
    
    print("\n【选择灵兽】")
    for i, b in enumerate(available, 1):
        print(f"{i}. {b.name} (HP:{b.hp}/{b.max_hp})")
    
    choice = input("选择: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(available):
        beast = available[int(choice) - 1]
        
        enemy_level = player.level
        result = BeastSystem.send_to_battle(beast, enemy_level)
        
        print("\n【战斗开始】")
        for log in result["log"]:
            print(log)
        
        if result["win"]:
            print(f"\n★★★ 战斗胜利! 灵兽获得{result['exp']:.1f}经验 ★★★")
            if result.get("evolution_available"):
                print(f">>> {beast.name} 可以进化了! <<<")
        else:
            print("\n💀 战斗失败... 💀")


def combined_battle(player: Player):
    """联手战斗"""
    if not player.beasts:
        print("\n暂无灵兽")
        return
    
    available = [b for b in player.beasts if b.hp > 0 and b.state == BeastState.IDLE]
    if not available:
        print("\n没有可战斗的灵兽")
        return
    
    enemy_level = player.level
    print(f"\n【联手战斗】你与{len(available)}只灵兽共同出战!")
    
    result = BeastSystem.get_combined_attack(player, available, enemy_level)
    
    if "error" in result:
        print(f"\n{result['error']}")
        return
    
    print("\n【战斗开始】")
    for log in result["log"]:
        print(log)
    
    if result["win"]:
        print(f"\n★★★ 战斗胜利! ★★★")
        print(f"总伤害: {result['damage_dealt']}")
        print(f"灵兽获得经验: {result['exp']:.1f}")
        print(f"获得灵石: {result['reward']}")
        player.spirit_stones += result['reward']
    else:
        print("\n💀 战斗失败... 💀")


def feed_beast(player: Player):
    """喂食灵兽"""
    if not player.beasts:
        print("\n暂无灵兽")
        return
    
    print("\n【选择灵兽】")
    for i, b in enumerate(player.beasts, 1):
        print(f"{i}. {b.name} (饱食度:{b.fullness}%)")
    
    choice = input("选择: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(player.beasts):
        beast = player.beasts[int(choice) - 1]
        
        print("\n选择食物:")
        print("1. 普通灵草 (10灵石)")
        print("2. 精品灵果 (30灵石)")
        print("3. 珍稀灵肉 (80灵石)")
        
        food_choice = input("选择: ").strip()
        food_quality = 1
        cost = 10
        
        if food_choice == "2":
            food_quality = 3
            cost = 30
        elif food_choice == "3":
            food_quality = 8
            cost = 80
        
        if player.spirit_stones < cost:
            print("灵石不足!")
            return
        
        player.spirit_stones -= cost
        result = beast.feed(food_quality)
        
        print(f"\n喂食成功!")
        print(f"亲密度: {result['intimacy'] - result['intimacy_gain']}% → {result['intimacy']}%")
        print(f"饱食度: {beast.fullness}%")


def evolution_beast(player: Player):
    """灵兽进化"""
    if not player.beasts:
        print("\n暂无灵兽")
        return
    
    print("\n【选择灵兽】")
    for i, b in enumerate(player.beasts, 1):
        can_evo = "可进化" if b.can_evolution() else "不可进化"
        print(f"{i}. {b.name} ({can_evo})")
    
    choice = input("选择: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(player.beasts):
        beast = player.beasts[int(choice) - 1]
        
        if beast.evolution():
            print(f"\n★★★ {beast.name} 进化成功! ★★★")
            print(f"进化阶段: {beast.evolution_stage}")
            print(beast.status())
        else:
            print("\n当前无法进化，需要更多经验")


def release_beast(player: Player):
    """放生灵兽"""
    if not player.beasts:
        print("\n暂无灵兽")
        return
    
    print("\n【选择灵兽】")
    for i, b in enumerate(player.beasts, 1):
        print(f"{i}. {b.name}")
    
    choice = input("选择: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(player.beasts):
        beast = player.beasts.pop(int(choice) - 1)
        print(f"\n{BeastSystem.release_beast(beast)}")


def sect_menu(player: Player):
    """宗门系统菜单"""
    while True:
        sect = SectSystem.get_player_sect(player.name)
        
        print("\n" + "=" * 50)
        print("       仙 途 - 宗 门 系 统")
        print("=" * 50)
        
        if sect:
            print(sect.status())
            print("\n【宗门行动】")
            print("1. 宗门任务")
            print("2. 贡献资源")
            print("3. 升级建筑")
            print("4. 宗门成员")
            print("5. 离开宗门")
        else:
            print("\n【当前状态】尚未加入宗门")
            print("\n【宗门行动】")
            print("1. 创建宗门")
            print("2. 加入宗门")
            print("3. 搜索宗门")
        
        print("0. 返回")
        
        choice = input("\n请选择: ").strip()
        
        if choice == "0":
            break
        elif sect:
            if choice == "1":
                sect_tasks_menu(player, sect)
            elif choice == "2":
                contribute_resources(player, sect)
            elif choice == "3":
                upgrade_building_menu(player, sect)
            elif choice == "4":
                list_sect_members(sect)
            elif choice == "5":
                leave_sect(player)
        else:
            if choice == "1":
                create_sect(player)
            elif choice == "2":
                join_sect(player)
            elif choice == "3":
                search_sects()


def sect_tasks_menu(player: Player, sect: Sect):
    """宗门任务菜单"""
    # 生成每日任务
    sect.generate_daily_tasks()
    
    while True:
        print("\n【宗门任务】")
        
        if not sect.tasks:
            print("暂无任务")
            break
        
        for i, task in enumerate(sect.tasks, 1):
            status = "✓" if task.is_completed else "○"
            print(f"{i}. [{status}] {task.title}")
            print(f"   {task.description}")
            print(f"   进度: {task.current_amount}/{task.required_amount}")
            print(f"   奖励: {task.reward_contribution}贡献, {task.reward_spirit_stones}灵石")
        
        print("\n0. 返回")
        
        choice = input("\n选择任务: ").strip()
        
        if choice == "0":
            break
        
        if choice.isdigit() and 1 <= int(choice) <= len(sect.tasks):
            task = sect.tasks[int(choice) - 1]
            
            if task.task_type == SectTaskType.CONTRIBUTION:
                print(f"\n{task.description}")
                amount = input("请输入贡献数量: ").strip()
                if amount.isdigit():
                    amount = int(amount)
                    result = SectSystem.contribute_resources(player.name, "herbs", amount)
                    if result["success"]:
                        task.current_amount += 1
                        if task.is_completed:
                            sect.add_contribution(player.name, task.reward_contribution)
                            print(f"任务完成! 获得{task.reward_contribution}贡献")
                        else:
                            print(f"进度: {task.current_amount}/{task.required_amount}")
                    else:
                        print(result["message"])
            elif task.task_type == SectTaskType.COMBAT:
                print(f"\n开始战斗: {task.description}")
                # 简单战斗
                enemy_hp = 50 + player.level * 20
                enemy_attack = 10 + player.level * 3
                
                while player.hp > 0 and enemy_hp > 0:
                    damage = player.attack
                    enemy_hp -= damage
                    print(f"你对敌人造成 {damage} 点伤害")
                    
                    if enemy_hp <= 0:
                        break
                    
                    actual = player.take_damage(enemy_attack)
                    print(f"敌人对你造成 {actual} 点伤害")
                
                if player.hp > 0:
                    task.current_amount = task.required_amount
                    sect.add_contribution(player.name, task.reward_contribution)
                    sect.spirit_stones += task.reward_spirit_stones
                    print(f"\n★★★ 任务完成! 获得{task.reward_contribution}贡献, {task.reward_spirit_stones}灵石 ★★★")
                    player.hp = player.max_hp
                else:
                    print("\n💀 战斗失败... 💀")
                    player.hp = player.max_hp


def contribute_resources(player: Player, sect: Sect):
    """贡献资源"""
    print("\n【贡献资源】")
    print("1. 贡献灵石 (100:1贡献)")
    print("2. 贡献药材 (10:1贡献)")
    print("3. 贡献材料 (10:1贡献)")
    
    choice = input("选择: ").strip()
    
    if choice == "1":
        amount = input("数量: ").strip()
        if amount.isdigit() and player.spirit_stones >= int(amount):
            player.spirit_stones -= int(amount)
            contribution = int(amount) // 100
            sect.add_contribution(player.name, contribution)
            print(f"贡献成功! 获得{contribution}贡献")
        else:
            print("灵石不足")
    elif choice == "2":
        amount = input("数量: ").strip()
        if amount.isdigit():
            contribution = int(amount) // 10
            sect.herbs += int(amount)
            sect.add_contribution(player.name, contribution)
            print(f"贡献成功! 获得{contribution}贡献")
    elif choice == "3":
        amount = input("数量: ").strip()
        if amount.isdigit():
            contribution = int(amount) // 10
            sect.materials += int(amount)
            sect.add_contribution(player.name, contribution)
            print(f"贡献成功! 获得{contribution}贡献")


def upgrade_building_menu(player: Player, sect: Sect):
    """升级建筑菜单"""
    while True:
        print("\n【升级建筑】")
        print(f"宗门灵石: {sect.spirit_stones}")
        print()
        
        # 显示所有可升级的建筑
        available = []
        for building_type, config in BUILDING_CONFIG.items():
            current = sect.buildings.get(building_type, SectBuildingData(building_type, 0))
            cost = current.upgrade_cost
            status = f"Lv.{current.level}" if current.level > 0 else "未建造"
            
            if current.level < current.config["max_level"]:
                available.append((building_type, config, cost, status))
                idx = len(available)
                print(f"{idx}. {config['name']} ({status}) -> Lv.{current.level + 1}")
                print(f"   升级费用: {cost}灵石")
                print(f"   效果: {config['effect']}")
            else:
                print(f"  ◆ {config['name']} (已满级)")
        
        print("\n0. 返回")
        
        choice = input("\n选择建筑: ").strip()
        
        if choice == "0":
            break
        
        if choice.isdigit() and 1 <= int(choice) <= len(available):
            building_type, config, cost, status = available[int(choice) - 1]
            
            if sect.spirit_stones >= cost:
                result = sect.upgrade_building(building_type)
                print(result["message"])
                
                # 升级增加宗门经验
                sect.add_exp(50)
            else:
                print("灵石不足")


def list_sect_members(sect: Sect):
    """查看宗门成员"""
    print("\n【宗门成员】")
    for member in sect.members.values():
        print(f"  • {member.name} ({member.rank.value})")
        print(f"    贡献: {member.contribution} | 本周: {member.weekly_contribution}")
        print(f"    加入时间: {member.joined_at}")


def create_sect(player: Player):
    """创建宗门"""
    if player.spirit_stones < 500:
        print("\n创建宗门需要500灵石")
        return
    
    name = input("宗门名称: ").strip()
    if not name:
        print("名称不能为空")
        return
    
    desc = input("宗门描述(可选): ").strip()
    
    player.spirit_stones -= 500
    sect = SectSystem.create_sect(player.name, player.name, name, desc)
    
    if sect:
        print(f"\n★★★ 宗门创建成功! ★★★")
        print(f"宗门名称: {sect.name}")
        print(f"掌门: {sect.leader_name}")
    else:
        print("\n创建失败")


def join_sect(player: Player):
    """加入宗门"""
    available = SectSystem.list_available_sects()
    
    if not available:
        print("\n暂无可加入的宗门")
        print("可以先创建宗门")
        return
    
    print("\n【可加入的宗门】")
    for i, sect in enumerate(available, 1):
        print(f"{i}. {sect.name}")
        print(f"   等级: {sect.level} | 成员: {sect.member_count}/{sect.max_members}")
        print(f"   描述: {sect.description or '无'}")
    
    choice = input("\n选择宗门: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(available):
        sect = available[int(choice) - 1]
        result = SectSystem.join_sect(player.name, player.name, sect.id)
        print(f"\n{result['message']}")


def leave_sect(player: Player):
    """离开宗门"""
    confirm = input("确定离开宗门? (y/n): ").strip().lower()
    if confirm == "y":
        result = SectSystem.leave_sect(player.name)
        print(f"\n{result['message']}")


def search_sects():
    """搜索宗门"""
    keyword = input("搜索关键词: ").strip()
    
    sects = SectSystem.list_sects()
    matched = [s for s in sects if keyword in s.name]
    
    if not matched:
        print("未找到匹配的宗门")
        return
    
    print(f"\n找到{len(matched)}个宗门:")
    for sect in matched:
        print(f"  • {sect.name} (等级{sect.level}, 成员{sect.member_count})")


from core.sect import SectSystem, Sect, SectBuilding, SectRank, BUILDING_CONFIG, SectTaskType
from core.equipment import EquipmentSystem, EquipmentSlot, EquipmentType, EquipmentQuality, generate_random_equipment, equipment_shop


# ========== 装备系统功能 ==========

def equipment_menu(player: Player):
    """装备系统菜单"""
    # 确保玩家有背包
    if not hasattr(player, 'inventory'):
        player.inventory = []
    
    while True:
        print("\n" + "=" * 50)
        print("       【装备系统】")
        print("=" * 50)
        
        # 显示当前装备
        print("\n【当前装备】")
        equipped = []
        for slot in EquipmentSlot:
            equip = getattr(player, slot.value, None)
            if equip:
                enhance_str = f" +{equip.enhancement_level}" if equip.enhancement_level > 0 else ""
                print(f"  {slot.value}: {equip.name}{enhance_str} ({equip.quality.name})")
                equipped.append((slot, equip))
        
        if not equipped:
            print("  未穿戴任何装备")
        
        # 显示装备总属性
        total_stats = EquipmentSystem.get_total_equipment_stats(player)
        if total_stats.attack or total_stats.defense or total_stats.hp:
            print("\n【装备加成属性】")
            stats_dict = total_stats.to_dict()
            for k, v in stats_dict.items():
                print(f"  {k}: {v}")
        
        print("\n【行动】")
        print("1. 查看背包")
        print("2. 穿戴装备")
        print("3. 卸下装备")
        print("4. 强化装备")
        print("5. 装备商店")
        print("6. 抽取装备")
        print("0. 返回")
        
        choice = input("\n请选择: ").strip()
        
        if choice == "1":
            view_inventory(player)
        elif choice == "2":
            equip_item(player)
        elif choice == "3":
            unequip_item(player)
        elif choice == "4":
            enhance_equipment(player)
        elif choice == "5":
            equipment_store(player)
        elif choice == "6":
            gacha_equipment(player)
        elif choice == "0":
            break


def view_inventory(player: Player):
    """查看背包"""
    if not player.inventory:
        print("\n背包为空")
        return
    
    print("\n【背包装备】")
    for i, equip in enumerate(player.inventory, 1):
        stats = equip.total_stats
        stats_dict = stats.to_dict()
        stats_str = " | ".join([f"{k}:{v}" for k, v in stats_dict.items()])
        
        enhance_str = f" +{equip.enhancement_level}" if equip.enhancement_level > 0 else ""
        element_str = f" [{equip.element}]" if equip.element else ""
        
        print(f"{i}. {equip.name}{enhance_str}{element_str} ({equip.quality.name})")
        print(f"   {stats_str}")
        print(f"   等级要求: {equip.level_required}")
        print()


def equip_item(player: Player):
    """穿戴装备"""
    if not player.inventory:
        print("\n背包为空")
        return
    
    print("\n【选择装备】")
    for i, equip in enumerate(player.inventory, 1):
        print(f"{i}. {equip.name} ({equip.quality.name})")
    
    choice = input("选择: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(player.inventory):
        equip = player.inventory[int(choice) - 1]
        
        success, msg = EquipmentSystem.equip(player, equip)
        print(f"\n{msg}")
        
        if success:
            # 从背包移除
            player.inventory.pop(int(choice) - 1)
            # 应用装备属性
            EquipmentSystem.apply_equipment_bonus(player)


def unequip_item(player: Player):
    """卸下装备"""
    print("\n【选择槽位】")
    for i, slot in enumerate(EquipmentSlot, 1):
        equip = getattr(player, slot.value, None)
        if equip:
            print(f"{i}. {slot.value}: {equip.name}")
    
    choice = input("选择: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(EquipmentSlot):
        slot = list(EquipmentSlot)[int(choice) - 1]
        equip = getattr(player, slot.value, None)
        
        if equip:
            # 卸下装备
            setattr(player, slot.value, None)
            # 放入背包
            player.inventory.append(equip)
            # 更新属性
            EquipmentSystem.apply_equipment_bonus(player)
            print(f"\n已卸下: {equip.name}")
        else:
            print("\n该槽位没有装备")


def enhance_equipment(player: Player):
    """强化装备"""
    # 获取所有可强化的装备（已装备+背包）
    all_equipment = []
    
    # 已装备
    for slot in EquipmentSlot:
        equip = getattr(player, slot.value, None)
        if equip:
            all_equipment.append(("装备中", equip))
    
    # 背包
    for i, equip in enumerate(player.inventory):
        all_equipment.append((f"背包{i+1}", equip))
    
    if not all_equipment:
        print("\n没有可强化的装备")
        return
    
    print("\n【选择装备】")
    for i, (location, equip) in enumerate(all_equipment, 1):
        cost = equip.get_enhancement_cost()
        cost_str = f"{cost}灵石" if cost > 0 else "已满级"
        print(f"{i}. {location}: {equip.name} +{equip.enhancement_level} (强化费用: {cost_str})")
    
    choice = input("选择: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(all_equipment):
        location, equip = all_equipment[int(choice) - 1]
        success, msg = equip.enhance(player)
        print(f"\n{msg}")
        
        if success:
            # 更新装备属性
            EquipmentSystem.apply_equipment_bonus(player)


def equipment_store(player: Player):
    """装备商店"""
    while True:
        print("\n【装备商店】")
        print(f"当前灵石: {player.spirit_stones}")
        print()
        
        # 按品质分类显示
        for quality in [EquipmentQuality.IMMORTAL, EquipmentQuality.CELESTIAL, EquipmentQuality.DIVINE, EquipmentQuality.SPIRIT, EquipmentQuality.MORTAL]:
            items = equipment_shop.get_items_by_quality(quality)
            if items:
                print(f"\n【{quality.name}】")
                for i, item in enumerate(items):
                    # 显示部分商品
                    if i < 5:
                        print(f"  {len([x for q in list(EquipmentQuality)[:list(EquipmentQuality).index(quality)] for x in equipment_shop.get_items_by_quality(q)]) + i + 1}. {item.equipment.name} - {item.price}灵石")
        
        print("\n0. 返回")
        
        choice = input("\n选择商品: ").strip()
        
        if choice == "0":
            break
        
        # 简化：直接随机购买
        if choice.isdigit():
            idx = int(choice) - 1
            # 获取所有商品
            all_items = equipment_shop.items
            if 0 <= idx < len(all_items):
                item = all_items[idx]
                success, msg = equipment_shop.buy(player, idx)
                print(f"\n{msg}")
                
                if success:
                    # 获得装备
                    player.inventory.append(item.equipment)


def gacha_equipment(player: Player):
    """抽取装备"""
    print("\n【抽取装备】")
    print("1. 单抽 (100灵石)")
    print("2. 十连抽 (900灵石)")
    
    choice = input("选择: ").strip()
    
    cost = 100 if choice == "1" else 900
    
    if player.spirit_stones < cost:
        print("\n灵石不足!")
        return
    
    player.spirit_stones -= cost
    
    count = 1 if choice == "1" else 10
    
    print(f"\n开始抽取...")
    for i in range(count):
        realm_level = list(player.realm.value if hasattr(player.realm, 'value') else player.realm).index(player.realm) + 1 if hasattr(player, 'realm') else 1
        equip = generate_random_equipment(realm_level)
        player.inventory.append(equip)
        print(f"  获得: {equip.name} ({equip.quality.name})")
    
    print(f"\n背包现有 {len(player.inventory)} 件装备")


# ========== 仙侣系统功能 ==========


def partner_menu(player: Player):
    """仙侣管理菜单"""
    if not hasattr(player, 'partners'):
        player.partners = []
    
    while True:
        print("\n" + "=" * 40)
        print("       【仙侣道侣系统】")
        print("=" * 40)
        print(PartnerSystem.get_partner_summary(player.partners))
        
        print("\n【行动】")
        print("1. 寻找仙侣")
        print("2. 查看仙侣详情")
        print("3. 双修")
        print("4. 赠送礼物")
        print("5. 并肩作战")
        print("6. 探访仙侣")
        print("7. 解除关系")
        print("0. 返回主菜单")
        
        choice = input("\n请选择: ").strip()
        
        if choice == "1":
            find_partner(player)
        elif choice == "2":
            view_partner(player)
        elif choice == "3":
            dual_cultivate(player)
        elif choice == "4":
            give_gift(player)
        elif choice == "5":
            joint_combat(player)
        elif choice == "6":
            visit_partner(player)
        elif choice == "7":
            break_bond(player)
        elif choice == "0":
            break


def find_partner(player: Player):
    """寻找仙侣"""
    if len(player.partners) >= 3:
        print("\n仙侣数量已达上限(3人)")
        return
    
    print("\n【寻找仙侣】")
    print("1. 随缘相遇")
    print("2. 主动寻觅 (更高境界)")
    
    choice = input("选择: ").strip()
    
    prefer_higher = (choice == "2")
    new_partner = PartnerSystem.find_partner(player.partners, player.realm.value, prefer_higher)
    
    print(f"\n★★★ 遇到一位修仙者: {new_partner.name} ★★★")
    print(new_partner.status())
    
    confirm = input("\n是否结为道侣? (y/n): ").strip().lower()
    if confirm == "y":
        player.partners.append(new_partner)
        print(f"\n★★★ 你们结为道侣，约定共同修炼! ★★★")
    else:
        print("\n你们擦肩而过...")


def view_partner(player: Player):
    """查看仙侣详情"""
    if not player.partners:
        print("\n暂无仙侣")
        return
    
    print("\n【选择仙侣】")
    for i, p in enumerate(player.partners, 1):
        print(f"{i}. {p.name}")
    
    choice = input("选择: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(player.partners):
        partner = player.partners[int(choice) - 1]
        print(partner.status())


def dual_cultivate(player: Player):
    """双修"""
    if not player.partners:
        print("\n暂无仙侣")
        return
    
    # 选择仙侣
    print("\n【选择仙侣】")
    available = [p for p in player.partners if p.state == PartnerState.IDLE]
    if not available:
        print("\n没有空闲的仙侣")
        return
    
    for i, p in enumerate(available, 1):
        print(f"{i}. {p.name} (HP:{p.hp}/{p.max_hp})")
    
    choice = input("选择: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(available):
        partner = available[int(choice) - 1]
        
        hours = input("双修时长 (小时): ").strip()
        hours = float(hours) if hours.replace(".", "").isdigit() and float(hours) > 0 else 1.0
        
        result = PartnerSystem.cultivate_together(player, partner, hours)
        
        if "error" in result:
            print(f"\n{result['error']}")
            return
        
        print(f"\n{result['message']}")
        
        if result.get("attr_gains"):
            print(f"属性提升: {', '.join(result['attr_gains'])}")
        
        affection = partner.get_affection_level()
        print(f"仙侣当前好感: {partner.affection}% ({affection.value})")


def give_gift(player: Player):
    """赠送礼物"""
    if not player.partners:
        print("\n暂无仙侣")
        return
    
    # 选择仙侣
    print("\n【选择仙侣】")
    for i, p in enumerate(player.partners, 1):
        print(f"{i}. {p.name}")
    
    choice = input("选择: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(player.partners):
        partner = player.partners[int(choice) - 1]
        
        # 显示礼物列表
        print("\n【可选礼物】")
        for i, gift in enumerate(PARTNER_GIFTS, 1):
            print(f"{i}. {gift.name} (+{gift.affection_gain}好感) - {gift.description}")
        
        gift_choice = input("选择礼物 (直接回车随机): ").strip()
        
        if gift_choice.isdigit() and 1 <= int(gift_choice) <= len(PARTNER_GIFTS):
            gift_name = PARTNER_GIFTS[int(gift_choice) - 1].name
        else:
            gift_name = None
        
        result = PartnerSystem.give_gift(partner, gift_name)
        
        if "error" in result:
            print(f"\n{result['error']}")
            return
        
        print(f"\n{result['message']}")
        
        if result.get("level_changed"):
            print(f"★★★ 好感等级提升到 {result['new_level']}! ★★★")


def joint_combat(player: Player):
    """并肩作战"""
    if not player.partners:
        print("\n暂无仙侣")
        return
    
    if player.hp <= 0:
        print("\n你已受伤，无法战斗")
        return
    
    available = [p for p in player.partners if p.hp > 0 and p.state == PartnerState.IDLE]
    if not available:
        print("\n没有可战斗的仙侣")
        return
    
    print(f"\n【并肩作战】你将与 {len(available)} 位仙侣联手对敌")
    
    enemy_level = player.level
    result = PartnerSystem.joint_combat(player, available, enemy_level)
    
    if "error" in result:
        print(f"\n{result['error']}")
        return
    
    print("\n【战斗开始】")
    for log in result["log"]:
        print(log)
    
    if result["win"]:
        print(f"\n★★★ 战斗胜利! 获得{result['reward']}灵石 ★★★")
    else:
        print("\n💀 战斗失败... 💀")


def visit_partner(player: Player):
    """探访仙侣"""
    if not player.partners:
        print("\n暂无仙侣")
        return
    
    print("\n【选择仙侣】")
    for i, p in enumerate(player.partners, 1):
        print(f"{i}. {p.name}")
    
    choice = input("选择: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(player.partners):
        partner = player.partners[int(choice) - 1]
        message = PartnerSystem.visit_partner(partner)
        print(f"\n{message}")
        
        # 探访也会增加少量好感
        if random.random() < 0.3:
            result = partner.update_affection(1)
            print(f"好感度微增: {partner.affection}%")


def break_bond(player: Player):
    """解除关系"""
    if not player.partners:
        print("\n暂无仙侣")
        return
    
    print("\n【选择仙侣】")
    for i, p in enumerate(player.partners, 1):
        print(f"{i}. {p.name}")
    
    choice = input("选择: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(player.partners):
        partner = player.partners.pop(int(choice) - 1)
        print(f"\n{PartnerSystem.break_bond(partner)}")


if __name__ == "__main__":
    # 加载或创建角色
    player = load_or_create_player()
    
    if player:
        main_menu(player)
