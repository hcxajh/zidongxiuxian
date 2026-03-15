"""
修仙游戏 - SQLite 数据库存储模块
支持玩家数据持久化存储和读取
"""

import sqlite3
import json
import os
from typing import Optional, List, Dict, Any
from datetime import datetime


# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(__file__), "game_data.db")


def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """初始化数据库表结构"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 玩家表 - 存储玩家核心数据
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            level INTEGER DEFAULT 1,
            realm TEXT DEFAULT 'MORTAL',
            qi REAL DEFAULT 0.0,
            max_qi REAL DEFAULT 100.0,
            hp REAL DEFAULT 100.0,
            max_hp REAL DEFAULT 100.0,
            spirit_stones INTEGER DEFAULT 100,
            cultivation REAL DEFAULT 0.0,
            total_cultivation REAL DEFAULT 0.0,
            attack INTEGER DEFAULT 10,
            defense INTEGER DEFAULT 5,
            cultivation_speed REAL DEFAULT 1.0,
            crit REAL DEFAULT 0.0,
            speed REAL DEFAULT 1.0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 灵根表 - 存储玩家的灵根信息
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_elements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            element_type TEXT NOT NULL,
            grade INTEGER NOT NULL,
            FOREIGN KEY (player_name) REFERENCES players(name) ON DELETE CASCADE
        )
    ''')
    
    # 功法表 - 存储玩家学习的功法
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            skill_id TEXT NOT NULL,
            level INTEGER DEFAULT 1,
            exp REAL DEFAULT 0.0,
            FOREIGN KEY (player_name) REFERENCES players(name) ON DELETE CASCADE
        )
    ''')
    
    # 装备表 - 存储玩家背包和已穿戴装备
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            slot TEXT,
            equipment_data TEXT NOT NULL,
            is_equipped INTEGER DEFAULT 0,
            FOREIGN KEY (player_name) REFERENCES players(name) ON DELETE CASCADE
        )
    ''')
    
    # 弟子表 - 存储玩家的弟子
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_disciples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            disciple_data TEXT NOT NULL,
            FOREIGN KEY (player_name) REFERENCES players(name) ON DELETE CASCADE
        )
    ''')
    
    # 灵兽表 - 存储玩家的灵兽
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_beasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            beast_data TEXT NOT NULL,
            FOREIGN KEY (player_name) REFERENCES players(name) ON DELETE CASCADE
        )
    ''')
    
    # 仙侣表 - 存储玩家的仙侣
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_partners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            partner_data TEXT NOT NULL,
            FOREIGN KEY (player_name) REFERENCES players(name) ON DELETE CASCADE
        )
    ''')
    
    # 历练记录表 - 存储玩家的副本通关记录
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS adventure_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            adventure_type TEXT NOT NULL,
            difficulty REAL NOT NULL,
            completed_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (player_name) REFERENCES players(name) ON DELETE CASCADE
        )
    ''')
    
    # 宗门关联表 - 记录玩家所属宗门
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_sect (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT UNIQUE NOT NULL,
            sect_name TEXT,
            sect_id TEXT,
            sect_contribution INTEGER DEFAULT 0,
            FOREIGN KEY (player_name) REFERENCES players(name) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"数据库初始化完成: {DB_PATH}")


def save_player(player) -> bool:
    """
    保存玩家数据到数据库
    返回是否成功
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 开启事务
        conn.execute("BEGIN TRANSACTION")
        
        # 1. 保存玩家核心数据
        cursor.execute('''
            INSERT OR REPLACE INTO players 
            (name, level, realm, qi, max_qi, hp, max_hp, spirit_stones,
             cultivation, total_cultivation, attack, defense, 
             cultivation_speed, crit, speed, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            player.name,
            player.level,
            player.realm.value if hasattr(player.realm, 'value') else str(player.realm),
            player.qi,
            player.max_qi,
            player.hp,
            player.max_hp,
            player.spirit_stones,
            player.cultivation,
            player.total_cultivation,
            player.attack,
            player.defense,
            player.cultivation_speed,
            player.crit,
            player.speed,
            datetime.now().isoformat()
        ))
        
        # 2. 保存灵根数据 (先删除旧的)
        cursor.execute("DELETE FROM player_elements WHERE player_name = ?", (player.name,))
        if player.elements:
            for elem in player.elements:
                elem_type = elem.type.value if hasattr(elem.type, 'value') else str(elem.type)
                elem_grade = elem.grade if hasattr(elem, 'grade') else 0
                cursor.execute(
                    "INSERT INTO player_elements (player_name, element_type, grade) VALUES (?, ?, ?)",
                    (player.name, elem_type, elem_grade)
                )
        
        # 3. 保存功法数据 (先删除旧的)
        cursor.execute("DELETE FROM player_skills WHERE player_name = ?", (player.name,))
        if player.skills:
            for skill_id, ps in player.skills.items():
                cursor.execute(
                    "INSERT INTO player_skills (player_name, skill_id, level, exp) VALUES (?, ?, ?, ?)",
                    (player.name, skill_id, ps.level, getattr(ps, 'exp', 0.0))
                )
        
        # 4. 保存装备数据 (先删除旧的)
        cursor.execute("DELETE FROM player_equipment WHERE player_name = ?", (player.name,))
        
        # 保存穿戴的装备
        equipment_slots = ['weapon', 'armor', 'helmet', 'boots', 'ring1', 'ring2', 'amulet', 'belt']
        for slot in equipment_slots:
            equip = getattr(player, slot, None)
            if equip:
                equip_data = serialize_equipment(equip)
                cursor.execute(
                    "INSERT INTO player_equipment (player_name, slot, equipment_data, is_equipped) VALUES (?, ?, ?, ?)",
                    (player.name, slot, json.dumps(equip_data), 1)
                )
        
        # 保存背包装备
        if hasattr(player, 'inventory') and player.inventory:
            for equip in player.inventory:
                equip_data = serialize_equipment(equip)
                cursor.execute(
                    "INSERT INTO player_equipment (player_name, slot, equipment_data, is_equipped) VALUES (?, ?, ?, ?)",
                    (player.name, 'inventory', json.dumps(equip_data), 0)
                )
        
        # 5. 保存弟子数据
        cursor.execute("DELETE FROM player_disciples WHERE player_name = ?", (player.name,))
        if hasattr(player, 'disciples') and player.disciples:
            for disciple in player.disciples:
                disciple_data = serialize_disciple(disciple)
                cursor.execute(
                    "INSERT INTO player_disciples (player_name, disciple_data) VALUES (?, ?)",
                    (player.name, json.dumps(disciple_data))
                )
        
        # 6. 保存灵兽数据
        cursor.execute("DELETE FROM player_beasts WHERE player_name = ?", (player.name,))
        if hasattr(player, 'beasts') and player.beasts:
            for beast in player.beasts:
                beast_data = serialize_beast(beast)
                cursor.execute(
                    "INSERT INTO player_beasts (player_name, beast_data) VALUES (?, ?)",
                    (player.name, json.dumps(beast_data))
                )
        
        # 7. 保存仙侣数据
        cursor.execute("DELETE FROM player_partners WHERE player_name = ?", (player.name,))
        if hasattr(player, 'partners') and player.partners:
            for partner in player.partners:
                partner_data = serialize_partner(partner)
                cursor.execute(
                    "INSERT INTO player_partners (player_name, partner_data) VALUES (?, ?)",
                    (player.name, json.dumps(partner_data))
                )
        
        # 8. 保存历练记录
        cursor.execute("DELETE FROM adventure_records WHERE player_name = ?", (player.name,))
        if hasattr(player, 'adventure_records') and player.adventure_records:
            for record_key, _ in player.adventure_records.items():
                parts = record_key.split('_')
                if len(parts) >= 2:
                    adventure_type = parts[0]
                    difficulty = float(parts[1]) if len(parts) > 1 else 1.0
                    cursor.execute(
                        "INSERT INTO adventure_records (player_name, adventure_type, difficulty) VALUES (?, ?, ?)",
                        (player.name, adventure_type, difficulty)
                    )
        
        conn.commit()
        conn.close()
        
        print(f"✓ 玩家 {player.name} 的数据已保存")
        return True
        
    except Exception as e:
        print(f"✗ 保存玩家数据失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def load_player(player_name: str):
    """
    从数据库加载玩家数据
    返回 Player 对象，如果不存在则返回 None
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 1. 加载玩家核心数据
        cursor.execute("SELECT * FROM players WHERE name = ?", (player_name,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        # 导入必要的类
        from core.player import Player, Realm
        from core.skill import PlayerSkill
        
        # 重建 Player 对象 - 需要通过 value 找到枚举
        realm_str = row['realm']
        realm = None
        for r in Realm:
            if r.value == realm_str:
                realm = r
                break
        if realm is None:
            realm = Realm.MORTAL  # 默认
        
        player = Player(
            name=row['name'],
            level=row['level'],
            realm=realm,
            qi=row['qi'],
            max_qi=row['max_qi'],
            hp=row['hp'],
            max_hp=row['max_hp'],
            spirit_stones=row['spirit_stones'],
            cultivation=row['cultivation'],
            total_cultivation=row['total_cultivation'],
            attack=row['attack'],
            defense=row['defense'],
            cultivation_speed=row['cultivation_speed'],
            crit=row['crit'],
            speed=row['speed']
        )
        
        # 2. 加载灵根数据
        cursor.execute("SELECT * FROM player_elements WHERE player_name = ?", (player_name,))
        from core.element import Element, ElementType
        player.elements = []
        for elem_row in cursor.fetchall():
            # 通过 value 找到枚举
            elem_str = elem_row['element_type']
            elem_type = None
            for et in ElementType:
                if et.value == elem_str:
                    elem_type = et
                    break
            if elem_type is None:
                continue  # 跳过未知的元素类型
            
            elem = Element(type=elem_type, grade=elem_row['grade'])
            player.elements.append(elem)
        
        # 应用灵根加成
        player.apply_element_bonuses()
        
        # 3. 加载功法数据
        cursor.execute("SELECT * FROM player_skills WHERE player_name = ?", (player_name,))
        from core.skill import SKILLS_DATABASE
        player.skills = {}
        for skill_row in cursor.fetchall():
            skill_id = skill_row['skill_id']
            level = skill_row['level']
            exp = skill_row['exp']
            if skill_id in SKILLS_DATABASE:
                player.skills[skill_id] = PlayerSkill(skill_id, level)
                if exp > 0 and hasattr(player.skills[skill_id], 'exp'):
                    player.skills[skill_id].exp = exp
        
        # 更新修炼速度
        from core.skill import SkillSystem
        player.cultivation_speed = SkillSystem.get_cultivation_bonus(player)
        
        # 4. 加载装备数据
        cursor.execute("SELECT * FROM player_equipment WHERE player_name = ?", (player_name,))
        player.inventory = []
        
        equipment_slots = ['weapon', 'armor', 'helmet', 'boots', 'ring1', 'ring2', 'amulet', 'belt']
        
        for equip_row in cursor.fetchall():
            equip_data = json.loads(equip_row['equipment_data'])
            equip = deserialize_equipment(equip_data)
            
            if equip_row['is_equipped']:
                slot = equip_row['slot']
                if slot in equipment_slots:
                    setattr(player, slot, equip)
            else:
                player.inventory.append(equip)
        
        # 应用装备属性
        from core.equipment import EquipmentSystem
        EquipmentSystem.apply_equipment_bonus(player)
        
        # 5. 加载弟子数据
        cursor.execute("SELECT * FROM player_disciples WHERE player_name = ?", (player_name,))
        player.disciples = []
        from core.disciple import Disciple
        for disc_row in cursor.fetchall():
            disc_data = json.loads(disc_row['disciple_data'])
            disciple = deserialize_disciple(disc_data)
            if disciple:
                player.disciples.append(disciple)
        
        # 6. 加载灵兽数据
        cursor.execute("SELECT * FROM player_beasts WHERE player_name = ?", (player_name,))
        player.beasts = []
        from core.beast import Beast
        for beast_row in cursor.fetchall():
            beast_data = json.loads(beast_row['beast_data'])
            beast = deserialize_beast(beast_data)
            if beast:
                player.beasts.append(beast)
        
        # 7. 加载仙侣数据
        cursor.execute("SELECT * FROM player_partners WHERE player_name = ?", (player_name,))
        player.partners = []
        from core.partner import Partner
        for partner_row in cursor.fetchall():
            partner_data = json.loads(partner_row['partner_data'])
            partner = deserialize_partner(partner_data)
            if partner:
                player.partners.append(partner)
        
        # 8. 加载历练记录
        cursor.execute("SELECT * FROM adventure_records WHERE player_name = ?", (player_name,))
        player.adventure_records = {}
        for rec_row in cursor.fetchall():
            record_key = f"{rec_row['adventure_type']}_{rec_row['difficulty']}"
            player.adventure_records[record_key] = True
        
        conn.close()
        
        print(f"✓ 玩家 {player_name} 的数据已加载")
        return player
        
    except Exception as e:
        print(f"✗ 加载玩家数据失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def list_saved_players() -> List[Dict[str, Any]]:
    """
    获取所有已保存的玩家列表
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT name, realm, level, spirit_stones, cultivation, updated_at 
        FROM players 
        ORDER BY updated_at DESC
    ''')
    
    players = []
    for row in cursor.fetchall():
        players.append({
            'name': row['name'],
            'realm': row['realm'],
            'level': row['level'],
            'spirit_stones': row['spirit_stones'],
            'cultivation': row['cultivation'],
            'updated_at': row['updated_at']
        })
    
    conn.close()
    return players


def delete_player(player_name: str) -> bool:
    """
    删除玩家数据
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 删除玩家 (级联删除会自动删除关联数据)
        cursor.execute("DELETE FROM players WHERE name = ?", (player_name,))
        
        conn.commit()
        conn.close()
        
        print(f"✓ 玩家 {player_name} 已删除")
        return True
        
    except Exception as e:
        print(f"✗ 删除玩家失败: {e}")
        return False


# ========== 序列化辅助函数 ==========

def serialize_equipment(equip) -> Dict:
    """序列化装备对象"""
    # EquipmentType 用 name (英文)，EquipmentQuality 用 name (中文质量名)
    data = {
        'id': getattr(equip, 'id', 'eq_' + str(id(equip))),
        'name': equip.name,
        'type': equip.type.name if hasattr(equip.type, 'name') else str(equip.type),
        'quality': equip.quality.name if hasattr(equip.quality, 'name') else str(equip.quality),
        'level_required': equip.level_required,
        'enhancement_level': getattr(equip, 'enhancement_level', 0),
        'enhancement_bonus': getattr(equip, 'enhancement_bonus', 0.0),
        'description': getattr(equip, 'description', ''),
        'element': str(getattr(equip, 'element', '')),
    }
    
    # 保存属性
    if hasattr(equip, 'base_stats'):
        bs = equip.base_stats
        data['base_stats'] = {
            'attack': bs.attack,
            'defense': bs.defense,
            'hp': bs.hp,
            'qi': bs.qi,
            'crit': bs.crit,
            'crit_damage': bs.crit_damage,
            'speed': bs.speed,
            'cultivation_speed': bs.cultivation_speed,
        }
    
    return data


def deserialize_equipment(data: Dict):
    """反序列化装备对象"""
    from core.equipment import Equipment, EquipmentType, EquipmentQuality, EquipmentStats
    
    # 查找枚举
    def find_enum(enum_class, key):
        # 先尝试用 key 匹配 name
        for e in enum_class:
            if e.name == key:
                return e
        # 再尝试匹配 value
        for e in enum_class:
            if hasattr(e, 'value') and e.value == key:
                return e
        # 默认返回第一个
        return list(enum_class)[0]
    
    eq_type = find_enum(EquipmentType, data.get('type', 'WEAPON'))
    eq_quality = find_enum(EquipmentQuality, data.get('quality', 'MORTAL'))
    
    # 创建基础属性
    base_stats = EquipmentStats()
    if 'base_stats' in data:
        bs = data['base_stats']
        base_stats.attack = bs.get('attack', 0)
        base_stats.defense = bs.get('defense', 0)
        base_stats.hp = bs.get('hp', 0)
        base_stats.qi = bs.get('qi', 0)
        base_stats.crit = bs.get('crit', 0.0)
        base_stats.crit_damage = bs.get('crit_damage', 0.0)
        base_stats.speed = bs.get('speed', 0.0)
        base_stats.cultivation_speed = bs.get('cultivation_speed', 0.0)
    
    equip = Equipment(
        id=data.get('id', 'eq_default'),
        name=data['name'],
        type=eq_type,
        quality=eq_quality,
        level_required=data.get('level_required', 1),
        base_stats=base_stats,
        enhancement_level=data.get('enhancement_level', 0),
        enhancement_bonus=data.get('enhancement_bonus', 0.0),
        description=data.get('description', ''),
        element=data.get('element', '')
    )
    
    return equip


def serialize_disciple(disciple) -> Dict:
    """序列化弟子对象"""
    return {
        'id': getattr(disciple, 'id', 'd_' + str(id(disciple))),
        'name': disciple.name,
        'realm': disciple.realm,
        'level': disciple.level,
        'hp': disciple.hp,
        'max_hp': disciple.max_hp,
        'attack': disciple.attack,
        'defense': disciple.defense,
        'state': disciple.state.value if hasattr(disciple, 'state') and hasattr(disciple.state, 'value') else 'IDLE',
    }


def deserialize_disciple(data: Dict):
    """反序列化弟子对象"""
    from core.disciple import Disciple, DiscipleState
    
    disciple = Disciple(id=data.get('id', 'd_default'), name=data['name'])
    disciple.realm = data.get('realm', '炼气期')
    disciple.level = data.get('level', 1)
    disciple.hp = data.get('hp', 100)
    disciple.max_hp = data.get('max_hp', 100)
    disciple.attack = data.get('attack', 10)
    disciple.defense = data.get('defense', 5)
    if 'state' in data:
        try:
            disciple.state = DiscipleState[data['state']]
        except:
            disciple.state = DiscipleState.IDLE
    
    return disciple


def serialize_beast(beast) -> Dict:
    """序列化灵兽对象"""
    return {
        'id': getattr(beast, 'id', 'b_' + str(id(beast))),
        'name': beast.name,
        'realm': beast.realm,
        'level': beast.level,
        'hp': beast.hp,
        'max_hp': beast.max_hp,
        'attack': beast.attack,
        'defense': beast.defense,
        'quality': beast.quality.name if hasattr(beast, 'quality') and hasattr(beast.quality, 'name') else 'NORMAL',
        'state': beast.state.name if hasattr(beast, 'state') and hasattr(beast.state, 'name') else 'IDLE',
        'fullness': getattr(beast, 'fullness', 100),
        'intimacy': getattr(beast, 'intimacy', 0),
        'evolution_stage': getattr(beast, 'evolution_stage', 0),
        'exp': getattr(beast, 'exp', 0),
    }


def deserialize_beast(data: Dict):
    """反序列化灵兽对象"""
    from core.beast import Beast, BeastState, BeastQuality, BeastType
    
    # 获取或默认灵兽类型
    beast_type = BeastType.SPIRIT
    if 'type' in data:
        try:
            beast_type = BeastType[data['type']]
        except:
            pass
    
    beast = Beast(id=data.get('id', 'b_default'), name=data['name'], type=beast_type)
    beast.realm = data.get('realm', '炼气期')
    beast.level = data.get('level', 1)
    beast.hp = data.get('hp', 100)
    beast.max_hp = data.get('max_hp', 100)
    beast.attack = data.get('attack', 10)
    beast.defense = data.get('defense', 5)
    
    if 'quality' in data:
        try:
            beast.quality = BeastQuality[data['quality']]
        except:
            beast.quality = BeastQuality.NORMAL
    
    if 'state' in data:
        try:
            beast.state = BeastState[data['state']]
        except:
            beast.state = BeastState.IDLE
    
    beast.fullness = data.get('fullness', 100)
    beast.intimacy = data.get('intimacy', 0)
    beast.evolution_stage = data.get('evolution_stage', 0)
    beast.exp = data.get('exp', 0)
    
    return beast


def serialize_partner(partner) -> Dict:
    """序列化仙侣对象"""
    return {
        'id': getattr(partner, 'id', 'p_' + str(id(partner))),
        'name': partner.name,
        'realm': partner.realm,
        'level': partner.level,
        'hp': partner.hp,
        'max_hp': partner.max_hp,
        'attack': partner.attack,
        'defense': partner.defense,
        'affection': getattr(partner, 'affection', 0),
        'state': partner.state.name if hasattr(partner, 'state') and hasattr(partner.state, 'name') else 'IDLE',
    }


def deserialize_partner(data: Dict):
    """反序列化仙侣对象"""
    from core.partner import Partner, PartnerState
    
    partner = Partner(id=data.get('id', 'p_default'), name=data['name'])
    partner.realm = data.get('realm', '炼气期')
    partner.level = data.get('level', 1)
    partner.hp = data.get('hp', 100)
    partner.max_hp = data.get('max_hp', 100)
    partner.attack = data.get('attack', 10)
    partner.defense = data.get('defense', 5)
    partner.affection = data.get('affection', 0)
    
    if 'state' in data:
        try:
            partner.state = PartnerState[data['state']]
        except:
            partner.state = PartnerState.IDLE
    
    return partner


# 初始化数据库
init_database()
