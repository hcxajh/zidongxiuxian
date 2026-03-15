"""
修仙游戏 - 宗门系统模块
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import random
from datetime import datetime


class SectRank(Enum):
    """宗门职位"""
    LEADER = "掌门"
    ELDER = "长老"
    CORE = "核心弟子"
    INNER = "内门弟子"
    OUTER = "外门弟子"
    DISCIPLE = "记名弟子"


class SectBuilding(Enum):
    """宗门建筑"""
    MAIN_HALL = "主殿"          # 宗门核心
    TRAINING_GROUND = "练功场"    # 修炼加成
    MEDICINE_HALL = "炼丹房"     # 炼丹效率
    FORGE_HALL = "炼器室"        # 炼器效率
    LIBRARY = "藏书阁"           # 功法研究
    TREASURY = "藏宝阁"          # 仓库容量
    SPIRITUAL_LAND = "灵田"      # 药材产出
    SPIRIT_MINE = "灵矿"         # 灵石产出
    DISCIPLE_HALL = "弟子堂"     # 收徒数量
    ARRAY_HALL = "护宗大阵"      # 防御加成


# 宗门建筑配置
BUILDING_CONFIG = {
    SectBuilding.MAIN_HALL: {
        "name": "主殿",
        "base_cost": 1000,
        "max_level": 10,
        "effect": "宗门等级上限",
        "level_effect": {1: 5, 2: 10, 3: 15, 4: 20, 5: 30, 6: 50, 7: 80, 8: 100, 9: 150, 10: 200}
    },
    SectBuilding.TRAINING_GROUND: {
        "name": "练功场",
        "base_cost": 500,
        "max_level": 10,
        "effect": "宗门成员修炼速度加成",
        "level_effect": {1: 0.05, 2: 0.10, 3: 0.15, 4: 0.20, 5: 0.25, 6: 0.30, 7: 0.35, 8: 0.40, 9: 0.45, 10: 0.50}
    },
    SectBuilding.MEDICINE_HALL: {
        "name": "炼丹房",
        "base_cost": 500,
        "max_level": 10,
        "effect": "炼丹成功率加成",
        "level_effect": {1: 0.05, 2: 0.10, 3: 0.15, 4: 0.20, 5: 0.25, 6: 0.30, 7: 0.35, 8: 0.40, 9: 0.45, 10: 0.50}
    },
    SectBuilding.FORGE_HALL: {
        "name": "炼器室",
        "base_cost": 500,
        "max_level": 10,
        "effect": "炼器成功率加成",
        "level_effect": {1: 0.05, 2: 0.10, 3: 0.15, 4: 0.20, 5: 0.25, 6: 0.30, 7: 0.35, 8: 0.40, 9: 0.45, 10: 0.50}
    },
    SectBuilding.LIBRARY: {
        "name": "藏书阁",
        "base_cost": 800,
        "max_level": 10,
        "effect": "功法研究速度加成",
        "level_effect": {1: 0.05, 2: 0.10, 3: 0.15, 4: 0.20, 5: 0.25, 6: 0.30, 7: 0.35, 8: 0.40, 9: 0.45, 10: 0.50}
    },
    SectBuilding.TREASURY: {
        "name": "藏宝阁",
        "base_cost": 300,
        "max_level": 10,
        "effect": "仓库容量",
        "level_effect": {1: 100, 2: 200, 3: 300, 4: 500, 5: 800, 6: 1000, 7: 1500, 8: 2000, 9: 3000, 10: 5000}
    },
    SectBuilding.SPIRITUAL_LAND: {
        "name": "灵田",
        "base_cost": 200,
        "max_level": 10,
        "effect": "每日药材产出",
        "level_effect": {1: 1, 2: 2, 3: 3, 4: 5, 5: 8, 6: 12, 7: 18, 8: 25, 9: 35, 10: 50}
    },
    SectBuilding.SPIRIT_MINE: {
        "name": "灵矿",
        "base_cost": 200,
        "max_level": 10,
        "effect": "每日灵石产出",
        "level_effect": {1: 10, 2: 20, 3: 30, 4: 50, 5: 80, 6: 120, 7: 180, 8: 250, 9: 350, 10: 500}
    },
    SectBuilding.DISCIPLE_HALL: {
        "name": "弟子堂",
        "base_cost": 400,
        "max_level": 10,
        "effect": "最大弟子数量",
        "level_effect": {1: 5, 2: 10, 3: 15, 4: 20, 5: 30, 6: 40, 7: 60, 8: 80, 9: 100, 10: 150}
    },
    SectBuilding.ARRAY_HALL: {
        "name": "护宗大阵",
        "base_cost": 600,
        "max_level": 10,
        "effect": "宗门战防御加成",
        "level_effect": {1: 0.05, 2: 0.10, 3: 0.15, 4: 0.20, 5: 0.25, 6: 0.30, 7: 0.35, 8: 0.40, 9: 0.45, 10: 0.50}
    },
}


class SectTaskType(Enum):
    """宗门任务类型"""
    CONTRIBUTION = "贡献任务"      # 提交资源
    COMBAT = "战斗任务"           # 击败敌人
    EXPLORE = "探索任务"          # 探索副本
    DEFEND = "防守任务"           # 宗门防御
    RESEARCH = "研究任务"          # 功法研究


@dataclass
class SectMember:
    """宗门成员"""
    player_id: str
    name: str
    rank: SectRank = SectRank.DISCIPLE
    contribution: int = 0          # 累计贡献
    weekly_contribution: int = 0   # 本周贡献
    joined_at: str = ""
    
    def __post_init__(self):
        if not self.joined_at:
            self.joined_at = datetime.now().strftime("%Y-%m-%d")


@dataclass
class SectBuildingData:
    """宗门建筑数据"""
    building_type: SectBuilding
    level: int = 1
    
    @property
    def config(self) -> dict:
        return BUILDING_CONFIG[self.building_type]
    
    @property
    def upgrade_cost(self) -> int:
        """升级所需灵石"""
        base = self.config["base_cost"]
        return int(base * (1.5 ** (self.level - 1)))
    
    @property
    def effect_value(self):
        """当前等级效果值"""
        return self.config["level_effect"].get(self.level, 0)
    
    def can_upgrade(self) -> bool:
        return self.level < self.config["max_level"]


@dataclass
class SectTask:
    """宗门任务"""
    id: str
    title: str
    description: str
    task_type: SectTaskType
    required_amount: int
    current_amount: int = 0
    reward_contribution: int = 10
    reward_spirit_stones: int = 0
    reward_items: List[str] = field(default_factory=list)
    expires_at: str = ""
    
    def __post_init__(self):
        if not self.expires_at:
            # 默认7天后过期
            from datetime import timedelta
            expire = datetime.now() + timedelta(days=7)
            self.expires_at = expire.strftime("%Y-%m-%d")
    
    @property
    def progress(self) -> float:
        return min(1.0, self.current_amount / self.required_amount)
    
    @property
    def is_completed(self) -> bool:
        return self.current_amount >= self.required_amount


@dataclass
class Sect:
    """宗门"""
    id: str
    name: str
    description: str = ""
    leader_id: str = ""           # 掌门ID
    leader_name: str = ""         # 掌门名称
    
    level: int = 1                # 宗门等级
    exp: int = 0                  # 宗门经验
    max_exp: int = 100            # 升级所需经验
    
    members: Dict[str, SectMember] = field(default_factory=dict)
    buildings: Dict[SectBuilding, SectBuildingData] = field(default_factory=dict)
    tasks: List[SectTask] = field(default_factory=list)
    
    # 资源
    spirit_stones: int = 0        # 宗门灵石
    herbs: int = 0                # 药材
    materials: int = 0            # 炼器材料
    
    # 设置
    join_requirement_level: int = 1    # 加入需要的境界层数
    is_recruiting: bool = True         # 是否开放加入
    
    created_at: str = ""
    last_daily_reset: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d")
        if not self.last_daily_reset:
            self.last_daily_reset = datetime.now().strftime("%Y-%m-%d")
        
        # 初始化建筑
        if not self.buildings and BUILDING_CONFIG:
            # 初始主殿1级，其他未建造
            self.buildings[SectBuilding.MAIN_HALL] = SectBuildingData(SectBuilding.MAIN_HALL, 1)
    
    @property
    def member_count(self) -> int:
        return len(self.members)
    
    @property
    def max_members(self) -> int:
        """最大成员数"""
        if SectBuilding.MAIN_HALL in self.buildings:
            return self.buildings[SectBuilding.MAIN_HALL].effect_value
        return 1
    
    @property
    def training_ground_bonus(self) -> float:
        """练功场修炼加成"""
        if SectBuilding.TRAINING_GROUND in self.buildings:
            return self.buildings[SectBuilding.TRAINING_GROUND].effect_value
        return 0.0
    
    def add_member(self, player_id: str, name: str, rank: SectRank = SectRank.DISCIPLE) -> bool:
        """添加成员"""
        if self.member_count >= self.max_members:
            return False
        
        if player_id in self.members:
            return False
        
        self.members[player_id] = SectMember(
            player_id=player_id,
            name=name,
            rank=rank
        )
        return True
    
    def remove_member(self, player_id: str) -> bool:
        """移除成员"""
        if player_id not in self.members:
            return False
        
        member = self.members[player_id]
        if member.rank == SectRank.LEADER:
            return False  # 不能移除掌门
        
        del self.members[player_id]
        return True
    
    def promote_member(self, player_id: str, new_rank: SectRank) -> bool:
        """晋升成员"""
        if player_id not in self.members:
            return False
        
        self.members[player_id].rank = new_rank
        return True
    
    def add_contribution(self, player_id: str, amount: int) -> bool:
        """添加贡献"""
        if player_id not in self.members:
            return False
        
        self.members[player_id].contribution += amount
        self.members[player_id].weekly_contribution += amount
        return True
    
    def upgrade_building(self, building_type: SectBuilding) -> dict:
        """升级建筑"""
        if building_type not in self.buildings:
            self.buildings[building_type] = SectBuildingData(building_type, 0)
        
        building = self.buildings[building_type]
        
        if not building.can_upgrade():
            return {"success": False, "message": f"{building.config['name']}已达最大等级"}
        
        cost = building.upgrade_cost
        if self.spirit_stones < cost:
            return {"success": False, "message": f"灵石不足，需要{cost}灵石"}
        
        self.spirit_stones -= cost
        building.level += 1
        
        return {
            "success": True, 
            "message": f"升级成功! {building.config['name']}现在是{building.level}级"
        }
    
    def add_exp(self, amount: int) -> dict:
        """增加宗门经验"""
        self.exp += amount
        
        leveled_up = []
        while self.exp >= self.max_exp and self.level < 10:
            self.exp -= self.max_exp
            self.level += 1
            self.max_exp = int(self.max_exp * 1.5)
            leveled_up.append(self.level)
        
        result = {"success": True, "exp_gained": amount}
        if leveled_up:
            result["leveled_up"] = leveled_up
            result["message"] = f"宗门升级! 当前等级: {self.level}"
        
        return result
    
    def generate_daily_tasks(self, force: bool = False):
        """生成每日任务"""
        today = datetime.now().strftime("%Y-%m-%d")
        if not force and self.last_daily_reset == today:
            return  # 今天已生成
        
        self.last_daily_reset = today
        self.tasks.clear()
        
        # 生成3-5个任务
        task_templates = [
            ("贡献任务", SectTaskType.CONTRIBUTION, "上交药材", 5, 10, 50),
            ("贡献任务", SectTaskType.CONTRIBUTION, "上交炼器材料", 5, 10, 50),
            ("贡献任务", SectTaskType.CONTRIBUTION, "捐献灵石", 100, 10, 20),
            ("战斗任务", SectTaskType.COMBAT, "击败筑基期修士", 1, 30, 100),
            ("战斗任务", SectTaskType.COMBAT, "击败金丹期修士", 1, 50, 200),
            ("探索任务", SectTaskType.EXPLORE, "探索灵气洞穴", 1, 40, 150),
            ("探索任务", SectTaskType.EXPLORE, "探索翠竹秘境", 1, 60, 300),
        ]
        
        num_tasks = random.randint(3, 5)
        selected = random.sample(task_templates, min(num_tasks, len(task_templates)))
        
        for i, (title, task_type, desc, req, cont, stones) in enumerate(selected):
            task_id = f"task_{today}_{i}"
            self.tasks.append(SectTask(
                id=task_id,
                title=title,
                description=desc,
                task_type=task_type,
                required_amount=req,
                reward_contribution=cont,
                reward_spirit_stones=stones
            ))
    
    def daily_production(self) -> dict:
        """每日产出"""
        today = datetime.now().strftime("%Y-%m-%d")
        if self.last_daily_reset != today:
            self.generate_daily_tasks()
        
        produced = {}
        
        # 灵田产出
        if SectBuilding.SPIRITUAL_LAND in self.buildings:
            herbs = self.buildings[SectBuilding.SPIRITUAL_LAND].effect_value
            self.herbs += herbs
            produced["herbs"] = herbs
        
        # 灵矿产出
        if SectBuilding.SPIRIT_MINE in self.buildings:
            stones = self.buildings[SectBuilding.SPIRIT_MINE].effect_value
            self.spirit_stones += stones
            produced["spirit_stones"] = stones
        
        return produced
    
    def status(self) -> str:
        """宗门状态"""
        members_list = []
        for m in self.members.values():
            members_list.append(f"  • {m.name} ({m.rank.value}) 贡献:{m.contribution}")
        
        buildings_list = []
        for b in self.buildings.values():
            buildings_list.append(f"  • {b.config['name']} Lv.{b.level}")
        
        return f"""
╔══════════════════════════════════════╗
║ 宗门: {self.name}                    ║
╠══════════════════════════════════════╣
║ 等级: {self.level} | 经验: {self.exp}/{self.max_exp}          ║
║ 成员: {self.member_count}/{self.max_members}                         ║
║ 灵石: {self.spirit_stones} | 药材: {self.herbs} | 材料: {self.materials}      ║
╠══════════════════════════════════════╣
║ 建筑:                                   ║
{chr(10).join(buildings_list) if buildings_list else '  无'}
╠══════════════════════════════════════╣
║ 成员:                                  ║
{chr(10).join(members_list) if members_list else '  无'}
╚══════════════════════════════════════╝
"""


# 全局宗门管理器
class SectSystem:
    """宗门系统管理器"""
    sects: Dict[str, Sect] = {}
    player_sect: Dict[str, str] = {}  # player_id -> sect_id
    
    @classmethod
    def create_sect(cls, leader_id: str, leader_name: str, sect_name: str, description: str = "") -> Sect:
        """创建宗门"""
        # 检查是否已有宗门
        if leader_id in cls.player_sect:
            return None
        
        # 生成ID
        sect_id = f"sect_{len(cls.sects)}_{int(datetime.now().timestamp())}"
        
        sect = Sect(
            id=sect_id,
            name=sect_name,
            description=description,
            leader_id=leader_id,
            leader_name=leader_name,
            level=1,
            spirit_stones=1000  # 初始资金
        )
        
        # 掌门加入
        sect.add_member(leader_id, leader_name, SectRank.LEADER)
        
        cls.sects[sect_id] = sect
        cls.player_sect[leader_id] = sect_id
        
        return sect
    
    @classmethod
    def join_sect(cls, player_id: str, player_name: str, sect_id: str) -> dict:
        """加入宗门"""
        if player_id in cls.player_sect:
            return {"success": False, "message": "你已有宗门"}
        
        if sect_id not in cls.sects:
            return {"success": False, "message": "宗门不存在"}
        
        sect = cls.sects[sect_id]
        
        if not sect.is_recruiting:
            return {"success": False, "message": "该宗门暂不开放加入"}
        
        if sect.member_count >= sect.max_members:
            return {"success": False, "message": "宗门成员已满"}
        
        if not sect.add_member(player_id, player_name, SectRank.DISCIPLE):
            return {"success": False, "message": "加入失败"}
        
        cls.player_sect[player_name] = sect_id
        
        return {"success": True, "message": f"成功加入{sect.name}!"}
    
    @classmethod
    def leave_sect(cls, player_id: str) -> dict:
        """离开宗门"""
        if player_id not in cls.player_sect:
            return {"success": False, "message": "你还没有宗门"}
        
        sect_id = cls.player_sect[player_id]
        
        if sect_id not in cls.sects:
            del cls.player_sect[player_id]
            return {"success": False, "message": "宗门不存在"}
        
        sect = cls.sects[sect_id]
        
        if not sect.remove_member(player_id):
            return {"success": False, "message": "掌门无法离开宗门，请先转让掌门"}
        
        del cls.player_sect[player_id]
        
        # 如果宗门空了，删除宗门
        if sect.member_count == 0:
            del cls.sects[sect_id]
        
        return {"success": True, "message": "已离开宗门"}
    
    @classmethod
    def get_player_sect(cls, player_id: str) -> Optional[Sect]:
        """获取玩家所在宗门"""
        sect_id = cls.player_sect.get(player_id)
        if sect_id:
            return cls.sects.get(sect_id)
        return None
    
    @classmethod
    def get_sect_by_name(cls, name: str) -> Optional[Sect]:
        """根据名称查找宗门"""
        for sect in cls.sects.values():
            if sect.name == name:
                return sect
        return None
    
    @classmethod
    def list_sects(cls) -> List[Sect]:
        """列出所有宗门"""
        return list(cls.sects.values())
    
    @classmethod
    def list_available_sects(cls) -> List[Sect]:
        """列出可加入的宗门"""
        return [s for s in cls.sects.values() if s.is_recruiting]
    
    @classmethod
    def get_sect_bonus(cls, player_id: str) -> dict:
        """获取玩家在宗门的加成"""
        sect = cls.get_player_sect(player_id)
        if not sect:
            return {"cultivation_bonus": 0.0, "medicine_bonus": 0.0, "forge_bonus": 0.0}
        
        return {
            "cultivation_bonus": sect.training_ground_bonus,
            "medicine_bonus": BUILDING_CONFIG[SectBuilding.MEDICINE_HALL]["level_effect"].get(
                sect.buildings.get(SectBuilding.MEDICINE_HALL, SectBuildingData(SectBuilding.MEDICINE_HALL, 0)).level, 0
            ),
            "forge_bonus": BUILDING_CONFIG[SectBuilding.FORGE_HALL]["level_effect"].get(
                sect.buildings.get(SectBuilding.FORGE_HALL, SectBuildingData(SectBuilding.FORGE_HALL, 0)).level, 0
            ),
        }
    
    @classmethod
    def contribute_resources(cls, player_id: str, resource_type: str, amount: int) -> dict:
        """贡献资源"""
        sect = cls.get_player_sect(player_id)
        if not sect:
            return {"success": False, "message": "你还没有宗门"}
        
        member = sect.members.get(player_id)
        if not member:
            return {"success": False, "message": "你不是宗门成员"}
        
        contribution = amount // 10  # 1/10转化为贡献点
        
        if resource_type == "spirit_stones":
            # 这里需要玩家对象，先假设传入的是玩家
            pass
        elif resource_type == "herbs":
            sect.herbs += amount
        elif resource_type == "materials":
            sect.materials += amount
        
        sect.add_contribution(player_id, contribution)
        
        return {
            "success": True, 
            "message": f"贡献成功! 获得{contribution}贡献点",
            "contribution": contribution
        }
    
    @classmethod
    def complete_task(cls, player_id: str, task_id: str, amount: int = 1) -> dict:
        """完成任务"""
        sect = cls.get_player_sect(player_id)
        if not sect:
            return {"success": False, "message": "你还没有宗门"}
        
        for task in sect.tasks:
            if task.id == task_id:
                if task.is_completed:
                    return {"success": False, "message": "任务已完成"}
                
                task.current_amount += amount
                
                if task.is_completed:
                    # 发放奖励
                    sect.add_contribution(player_id, task.reward_contribution)
                    sect.spirit_stones += task.reward_spirit_stones
                    
                    return {
                        "success": True,
                        "message": f"任务完成! 获得{task.reward_contribution}贡献点, {task.reward_spirit_stones}灵石",
                        "completed": True
                    }
                
                return {
                    "success": True,
                    "message": f"进度: {task.current_amount}/{task.required_amount}",
                    "completed": False
                }
        
        return {"success": False, "message": "任务不存在"}
