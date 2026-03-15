# 地图与副本数据

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
from core.player import Realm


class MapRegionType(Enum):
    """地图区域类型"""
    CITY = "城池"        # 安全区，可交易
    WILDERNESS = "野外"  # 历练区，可战斗
    CAVE = "洞府"        # 副本入口
    SECRET = "秘境"      # 限时/隐藏副本


class DungeonDifficulty(Enum):
    """副本难度"""
    EASY = "简单"
    NORMAL = "普通"
    HARD = "困难"
    NIGHTMARE = "噩梦"


@dataclass
class MapNode:
    """地图节点"""
    id: str
    name: str
    description: str
    region_type: MapRegionType
    min_realm: Realm  # 最低进入境界
    available: bool = True
    enemies: List[str] = None  # 敌人ID列表
    
    def __post_init__(self):
        if self.enemies is None:
            self.enemies = []


@dataclass
class Dungeon:
    """副本"""
    id: str
    name: str
    description: str
    region_type: MapRegionType
    min_realm: Realm
    difficulty: DungeonDifficulty
    
    # 敌人配置
    enemies: List[Dict] = None  # [{"realm": Realm, "level": 1-10, "count": 1-5}]
    
    # 奖励
    rewards: Dict = None  # {"spirit_stones": (min, max), "items": [...], "qi": (min, max)}
    
    # 通关奖励（首次通关）
    first_clear_reward: Dict = None
    
    def __post_init__(self):
        if self.enemies is None:
            self.enemies = []
        if self.rewards is None:
            self.rewards = {}
        if self.first_clear_reward is None:
            self.first_clear_reward = {}


# ============ 地图节点数据 ============

MAP_NODES = {
    # 凡人界
    "mortal_village": MapNode(
        id="mortal_village",
        name="青石村",
        description="凡人村落，民风淳朴，可在此休整",
        region_type=MapRegionType.CITY,
        min_realm=Realm.MORTAL,
    ),
    "mortal_mountain": MapNode(
        id="mortal_mountain",
        name="青牛山",
        description="常有野兽出没，适合初学者历练",
        region_type=MapRegionType.WILDERNESS,
        min_realm=Realm.MORTAL,
        enemies=["wild_beast"],
    ),
    
    # 炼气期
    "qi_lingyan Peak": MapNode(
        id="qi_lingyan_peak",
        name="凌云峰",
        description="灵气充裕，是炼气期修士的常见修炼之地",
        region_type=MapRegionType.WILDERNESS,
        min_realm=Realm.QI_REFINING,
        enemies=["qi_cultivator", "spirit_beast"],
    ),
    "qi_cave_1": MapNode(
        id="qi_cave_1",
        name="灵气洞穴",
        description="蕴含丰富灵气的地下洞穴",
        region_type=MapRegionType.CAVE,
        min_realm=Realm.QI_REFINING,
    ),
    
    # 筑基期
    "foundation_cloud_city": MapNode(
        id="foundation_cloud_city",
        name="白云城",
        description="筑基修士聚集的修仙城池",
        region_type=MapRegionType.CITY,
        min_realm=Realm.FOUNDATION,
    ),
    "foundation_bamboo_forest": MapNode(
        id="foundation_bamboo_forest",
        name="翠竹林",
        description="竹林深处有妖修出没",
        region_type=MapRegionType.WILDERNESS,
        min_realm=Realm.FOUNDATION,
        enemies=["bamboo_spirit", "snake_demon"],
    ),
    
    # 金丹期
    "gold_core_fire_mountain": MapNode(
        id="gold_core_fire_mountain",
        name="火焰山",
        description="火山地带，温度极高，金丹期修士方可进入",
        region_type=MapRegionType.WILDERNESS,
        min_realm=Realm.GOLDEN_CORE,
        enemies=["fire_elemental", "magma_golem"],
    ),
    
    # 元婴期
    "nasent_soul_void": MapNode(
        id="nasent_soul_void",
        name="虚空裂缝",
        description="空间不稳定，只有元婴期修士能存活",
        region_type=MapRegionType.SECRET,
        min_realm=Realm.NASENT_SOUL,
    ),
    
    # 化神期
    "transformation_celestial": MapNode(
        id="transformation_celestial",
        name="登天路",
        description="通往仙界的道路，化神期修士的最终考验",
        region_type=MapRegionType.SECRET,
        min_realm=Realm.TRANSFORMATION,
    ),
}


# ============ 副本数据 ============

DUNGEONS = {
    # 炼气期副本
    "qi_cave_exploration": Dungeon(
        id="qi_cave_exploration",
        name="灵气洞穴探险",
        description="探索神秘的地下洞穴，寻找天材地宝",
        region_type=MapRegionType.CAVE,
        min_realm=Realm.QI_REFINING,
        difficulty=DungeonDifficulty.EASY,
        enemies=[
            {"realm": Realm.QI_REFINING, "level_range": (1, 3), "count": 3},
            {"realm": Realm.QI_REFINING, "level_range": (4, 6), "count": 2},
            {"realm": Realm.QI_REFINING, "level_range": (7, 10), "count": 1},
        ],
        rewards={
            "spirit_stones": (10, 50),
            "qi": (20, 50),
        },
        first_clear_reward={
            "spirit_stones": 100,
            "items": ["qi_pill_basic"],
        },
    ),
    
    "qi_forest_trial": Dungeon(
        id="qi_forest_trial",
        name="翠林试炼",
        description="密林中的试炼，击败守护者获得灵药",
        region_type=MapRegionType.WILDERNESS,
        min_realm=Realm.QI_REFINING,
        difficulty=DungeonDifficulty.NORMAL,
        enemies=[
            {"realm": Realm.QI_REFINING, "level_range": (5, 8), "count": 3},
            {"realm": Realm.QI_REFINING, "level_range": (9, 10), "count": 2},
        ],
        rewards={
            "spirit_stones": (30, 80),
            "qi": (50, 100),
            "items": ["spiritual_herb"],
        },
        first_clear_reward={
            "items": ["foundation_pill"],
        },
    ),
    
    # 筑基期副本
    "foundation_cave": Dungeon(
        id="foundation_cave",
        name="筑基洞府",
        description="某位筑基期前辈的坐化洞府",
        region_type=MapRegionType.CAVE,
        min_realm=Realm.FOUNDATION,
        difficulty=DungeonDifficulty.NORMAL,
        enemies=[
            {"realm": Realm.FOUNDATION, "level_range": (1, 4), "count": 3},
            {"realm": Realm.FOUNDATION, "level_range": (5, 8), "count": 3},
            {"realm": Realm.FOUNDATION, "level_range": (9, 10), "count": 1},
        ],
        rewards={
            "spirit_stones": (100, 300),
            "qi": (100, 200),
            "items": ["foundation_ingredient"],
        },
        first_clear_reward={
            "spirit_stones": 500,
            "items": ["foundation_pill", "fire_attack_skill"],
        },
    ),
    
    "foundation_bamboo_secret": Dungeon(
        id="foundation_bamboo_secret",
        name="翠竹秘境",
        description="隐藏于竹林中的秘境，可能有大机遇",
        region_type=MapRegionType.SECRET,
        min_realm=Realm.FOUNDATION,
        difficulty=DungeonDifficulty.HARD,
        enemies=[
            {"realm": Realm.FOUNDATION, "level_range": (7, 10), "count": 5},
        ],
        rewards={
            "spirit_stones": (200, 500),
            "qi": (200, 400),
            "items": ["bamboo_heart", "ice_attack_skill"],
        },
        first_clear_reward={
            "items": ["rare_equipment_blue"],
        },
    ),
    
    # 金丹期副本
    "gold_core_volcano": Dungeon(
        id="gold_core_volcano",
        name="火山遗迹",
        description="上古修士留下的遗迹，危机四伏",
        region_type=MapRegionType.CAVE,
        min_realm=Realm.GOLDEN_CORE,
        difficulty=DungeonDifficulty.HARD,
        enemies=[
            {"realm": Realm.GOLDEN_CORE, "level_range": (1, 4), "count": 4},
            {"realm": Realm.GOLDEN_CORE, "level_range": (5, 8), "count": 4},
            {"realm": Realm.GOLDEN_CORE, "level_range": (9, 10), "count": 2},
        ],
        rewards={
            "spirit_stones": (500, 1000),
            "qi": (300, 600),
            "items": ["fire_essence", "gold_core_material"],
        },
        first_clear_reward={
            "spirit_stones": 2000,
            "items": ["gold_core_pill", "fire_immortal_skill"],
        },
    ),
    
    # 元婴期副本
    "nasent_soul_void_dungeon": Dungeon(
        id="nasent_soul_void_dungeon",
        name="虚空历练",
        description="在虚空裂缝中存活并寻找机遇",
        region_type=MapRegionType.SECRET,
        min_realm=Realm.NASENT_SOUL,
        difficulty=DungeonDifficulty.NIGHTMARE,
        enemies=[
            {"realm": Realm.NASENT_SOUL, "level_range": (1, 5), "count": 5},
            {"realm": Realm.NASENT_SOUL, "level_range": (6, 10), "count": 5},
        ],
        rewards={
            "spirit_stones": (1000, 3000),
            "qi": (500, 1000),
            "items": ["void_crystal", "soul_fruit"],
        },
        first_clear_reward={
            "items": ["nasent_soul_pill", "void_walk_skill"],
        },
    ),
    
    # 化神期副本
    "transformation_trial": Dungeon(
        id="transformation_trial",
        name="登天试炼",
        description="化神期的最终考验，通往仙界",
        region_type=MapRegionType.SECRET,
        min_realm=Realm.TRANSFORMATION,
        difficulty=DungeonDifficulty.NIGHTMARE,
        enemies=[
            {"realm": Realm.TRANSFORMATION, "level_range": (1, 5), "count": 10},
            {"realm": Realm.TRANSFORMATION, "level_range": (6, 10), "count": 10},
        ],
        rewards={
            "spirit_stones": (5000, 10000),
            "qi": (1000, 2000),
            "items": ["immortal_essence", "celestial_herb"],
        },
        first_clear_reward={
            "items": ["immortal_title"],
        },
    ),
}


def get_available_dungeons(realm: Realm) -> List[Dict]:
    """获取玩家可进入的副本列表"""
    available = []
    realm_index = list(Realm).index(realm)
    
    for dungeon in DUNGEONS.values():
        min_index = list(Realm).index(dungeon.min_realm)
        if min_index <= realm_index:
            available.append({
                "id": dungeon.id,
                "name": dungeon.name,
                "difficulty": dungeon.difficulty.value,
                "description": dungeon.description,
            })
    
    return available


def get_available_map_nodes(realm: Realm) -> List[MapNode]:
    """获取玩家可进入的地图节点"""
    available = []
    realm_index = list(Realm).index(realm)
    
    for node in MAP_NODES.values():
        min_index = list(Realm).index(node.min_realm)
        if min_index <= realm_index:
            available.append(node)
    
    return available
