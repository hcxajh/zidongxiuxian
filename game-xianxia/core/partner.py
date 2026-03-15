"""
修仙游戏 - 仙侣系统
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import random


class PartnerType(Enum):
    """仙侣类型"""
    CULTIVATOR = "修道者"      # 同道中人
    IMMORTAL = "仙人"           # 上界仙人
    DEMON = "妖魔"              # 妖修/魔修
    SPIRIT = "精灵"             # 天地精灵
    GHOST = "鬼修"              # 鬼道修士
    DRAGON = "龙族"             # 龙族伴侣
    PHOENIX = "凤凰"            # 凤凰族
    UNKNOWN = "神秘存在"


class PartnerQuality(Enum):
    """仙侣品质/资质"""
    MORTAL = 1      # 凡人
    QI_REFINE = 2   # 炼气
    FOUNDATION = 3   # 筑基
    GOLDEN_CORE = 4  # 金丹
    NASENT_SOUL = 5  # 元婴
    TRANSFORMATION = 6 # 化神
    VOID = 7         # 合体
    DHARMA = 8       # 大乘
    IMMORTAL = 9     # 仙人


class PartnerState(Enum):
    """仙侣状态"""
    IDLE = "空闲"
    CULTIVATING = "双修中"
    COMBAT = "并肩作战"
    SEPARATED = "分离"


class AffectionLevel(Enum):
    """好感等级"""
    ESTRANGED = "陌生人"       # 0-20
    ACQUAINTANCE = "相识"       # 21-40
    FRIEND = "朋友"             # 41-60
    CLOSE = "知己"              # 61-80
    BELOVED = "伴侣"            # 81-95
    SOULMATE = "道侣"           # 96-100


class DualCultivationSkill(Enum):
    """双修技能"""
    QI_MERGING = "灵气交融"     # 修炼效率提升
    SPIRIT_LINK = "神识链接"     # 战斗配合
    LIFE_SHARING = "生命共享"    # 受伤分担
    RESONANCE = "灵气共鸣"       # 突破加成
    HEART_SYNC = "心有灵犀"     # 暴击率提升


@dataclass
class PartnerGift:
    """礼物"""
    name: str
    affection_gain: int
    description: str


# 礼物库
PARTNER_GIFTS = [
    PartnerGift("同心玉佩", 15, "象征同心永结"),
    PartnerGift("并蒂莲花", 12, "象征百年好合"),
    PartnerGift("红线手绳", 10, "月老红线"),
    PartnerGift("灵花", 8, "蕴含灵气的花朵"),
    PartnerGift("灵果", 6, "鲜美多汁的灵果"),
    PartnerGift("情诗", 5, "亲手写的情诗"),
    PartnerGift("灵石", 3, "实用的修炼资源"),
]


@dataclass
class Partner:
    """仙侣"""
    id: str
    name: str
    partner_type: PartnerType
    
    # 资质/品质
    quality: PartnerQuality = PartnerQuality.MORTAL
    
    # 境界
    level: int = 1
    realm: str = "凡人"
    
    # 好感度
    affection: int = 50
    
    # 状态
    state: PartnerState = PartnerState.IDLE
    
    # 战斗属性
    attack: int = 8
    defense: int = 5
    hp: int = 80
    max_hp: int = 80
    qi: int = 60
    max_qi: int = 60
    
    # 特殊属性
    crit: float = 0.08
    speed: float = 1.1
    cultivation_boost: float = 0.15  # 双修加成
    
    # 灵根属性
    elements: List[str] = field(default_factory=list)
    
    # 绑定技能
    skills: List[str] = field(default_factory=list)
    
    # 专属功法
    technique: str = ""
    
    # 记忆回忆
    memories: List[str] = field(default_factory=list)
    
    # 命运纠缠度 (影响双修效果)
    fate: int = 30
    
    # 最后双修时间
    last_cultivation: float = 0.0
    
    # 结缘日期
    bound_date: str = ""
    
    def get_affection_level(self) -> AffectionLevel:
        """获取好感等级"""
        if self.affection >= 96:
            return AffectionLevel.SOULMATE
        elif self.affection >= 81:
            return AffectionLevel.BELOVED
        elif self.affection >= 61:
            return AffectionLevel.CLOSE
        elif self.affection >= 41:
            return AffectionLevel.FRIEND
        elif self.affection >= 21:
            return AffectionLevel.ACQUAINTANCE
        else:
            return AffectionLevel.ESTRANGED
    
    def get_quality_name(self) -> str:
        """获取品质名称"""
        names = {
            PartnerQuality.MORTAL: "凡人",
            PartnerQuality.QI_REFINE: "炼气",
            PartnerQuality.FOUNDATION: "筑基",
            PartnerQuality.GOLDEN_CORE: "金丹",
            PartnerQuality.NASENT_SOUL: "元婴",
            PartnerQuality.TRANSFORMATION: "化神",
            PartnerQuality.VOID: "合体",
            PartnerQuality.DHARMA: "大乘",
            PartnerQuality.IMMORTAL: "仙人",
        }
        return names.get(self.quality, "凡人")
    
    def get_type_name(self) -> str:
        """获取类型名称"""
        return self.partner_type.value
    
    def can_cultivate(self) -> bool:
        """是否可以双修"""
        return self.state == PartnerState.IDLE and self.hp > 0
    
    def update_affection(self, change: int) -> Dict:
        """更新好感度"""
        old_level = self.get_affection_level()
        self.affection = max(0, min(100, self.affection + change))
        new_level = self.get_affection_level()
        
        level_up = old_level != new_level
        
        return {
            "old_affection": self.affection - change,
            "new_affection": self.affection,
            "level_changed": level_up,
            "new_level": new_level.value
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
    
    def gain_fate(self, amount: int) -> int:
        """增加命运纠缠度"""
        self.fate = min(100, self.fate + amount)
        return self.fate
    
    def status(self) -> str:
        """状态显示"""
        affection = self.get_affection_level()
        elements_str = ", ".join(self.elements) if self.elements else "无"
        skills_str = ", ".join(self.skills) if self.skills else "无"
        
        return f"""
【{self.name}】({self.get_type_name()})
  资质: {self.get_quality_name()} | 境界: {self.realm}第{self.level}层
  好感: {self.affection}% ({affection.value})
  命运纠缠: {self.fate}%
  HP: {self.hp}/{self.max_hp} | Qi: {self.qi}/{self.max_qi}
  攻击: {self.attack} | 防御: {self.defense}
  暴击: {self.crit*100:.0f}% | 速度: {self.speed:.1f}x
  灵根: {elements_str}
  技能: {skills_str}
  双修加成: +{self.cultivation_boost*100:.0f}%
  状态: {self.state.value}
"""


class PartnerSystem:
    """仙侣管理系统"""
    
    # 仙侣名字库
    MALE_NAMES = ["云渊", "风轩", "墨白", "青玄", "紫霄", "赤羽", "蓝泽", "青岚", 
                  "玉衡", "天澜", "星辰", "明轩", "清衍", "玄翼", "凌霄", "逸尘"]
    FEMALE_NAMES = ["云汐", "风晴", "墨璃", "青璃", "紫萱", "赤练", "蓝烟", "青璇",
                    "玉蓉", "天雪", "星瑶", "明玉", "清韵", "玄月", "凌雪", "逸梦"]
    
    # 通用名字
    NEUTRAL_NAMES = ["忘尘", "归隐", "逍遥", "飘渺", "无邪", "红尘", "问道", "寻道",
                     "天机", "宿命", "轮回", "因果", "缘起", "缘灭", "相思", "断肠"]
    
    # 类型对应名字
    TYPE_NAMES = {
        PartnerType.CULTIVATOR: {"prefix": ["青云", "玄冰", "烈焰", "幽冥", "天雷"],
                                 "suffix": ["子", "仙子", "真人", "道君"]},
        PartnerType.IMMORTAL: {"prefix": ["九", "太", "玉", "金", "紫"],
                               "suffix": ["元君", "上仙", "真君", "仙子"]},
        PartnerType.DEMON: {"prefix": ["魔", "妖", "邪", "幽", "血"],
                            "suffix": ["皇", "帝", "君", "主"]},
        PartnerType.SPIRIT: {"prefix": ["灵", "精", "魅", "仙", "云"],
                             "suffix": ["儿", "君", "使", "灵"]},
        PartnerType.GHOST: {"prefix": ["幽", "魂", "鬼", "魇", "冥"],
                           "suffix": ["君", "使", "主", "帝"]},
        PartnerType.DRAGON: {"prefix": ["敖", "青龙", "白龙", "金龙", "应龙"],
                            "suffix": ["太子", "公主", "皇子", "龙君"]},
        PartnerType.PHOENIX: {"prefix": ["朱", "青", "火", "彩", "金"],
                             "suffix": ["公主", "皇子", "帝姬", "仙子"]},
        PartnerType.UNKNOWN: {"prefix": ["神秘", "未知", "隐", "虚"],
                             "suffix": ["道人", "行者", "居士", "散人"]},
    }
    
    # 技能库
    SKILL_POOL = [
        "灵气交融", "神识链接", "生命共享", "灵气共鸣", 
        "心有灵犀", "阴阳调和", "太极两仪", "道法自然",
        "剑心通明", "琴瑟和鸣", "书画双绝", "棋道通天"
    ]
    
    # 功法库
    TECHNIQUE_POOL = [
        "双修大法", "阴阳和合经", "琴瑟合鸣诀", "比翼双飞功",
        "连理枝心法", "同心同德术", "道侣同心诀", "鸾凤和鸣典"
    ]
    
    @staticmethod
    def generate_partner(
        partner_type: PartnerType = None, 
        realm_level: int = 1,
        gender: str = "female"
    ) -> Partner:
        """生成随机仙侣"""
        # 随机类型
        if partner_type is None:
            partner_type = random.choice(list(PartnerType))
        
        # 生成ID
        partner_id = f"partner_{random.randint(10000, 99999)}"
        
        # 生成名字
        if partner_type == PartnerType.CULTIVATOR:
            if gender == "male":
                name = random.choice(PartnerSystem.MALE_NAMES)
            else:
                name = random.choice(PartnerSystem.FEMALE_NAMES)
        else:
            name = random.choice(PartnerSystem.NEUTRAL_NAMES)
        
        # 根据境界确定品质
        quality_map = {
            1: PartnerQuality.QI_REFINE,
            2: PartnerQuality.FOUNDATION,
            3: PartnerQuality.GOLDEN_CORE,
            4: PartnerQuality.NASENT_SOUL,
            5: PartnerQuality.TRANSFORMATION,
            6: PartnerQuality.VOID,
            7: PartnerQuality.DHARMA,
            8: PartnerQuality.IMMORTAL,
        }
        quality = quality_map.get(realm_level, PartnerQuality.QI_REFINE)
        
        # 境界名称
        realm_names = ["凡人", "炼气期", "筑基期", "金丹期", "元婴期", 
                      "化神期", "合体期", "大乘期", "仙人"]
        realm = realm_names[min(realm_level, len(realm_names) - 1)]
        
        # 根据品质设置属性
        quality_multiplier = 1.0 + (quality.value - 1) * 0.2
        base_hp = int((60 + realm_level * 10) * quality_multiplier)
        base_attack = int((8 + realm_level * 2) * quality_multiplier)
        base_defense = int((5 + realm_level * 1.5) * quality_multiplier)
        
        # 创建仙侣
        partner = Partner(
            id=partner_id,
            name=name,
            partner_type=partner_type,
            quality=quality,
            level=realm_level,
            realm=realm,
            hp=base_hp,
            max_hp=base_hp,
            qi=base_hp // 2,
            max_qi=base_hp // 2,
            attack=base_attack,
            defense=base_defense,
        )
        
        # 随机灵根
        elements_pool = ["金", "木", "水", "火", "土", "雷", "冰", "风"]
        num_elements = random.randint(1, 2)
        partner.elements = random.sample(elements_pool, num_elements)
        
        # 随机技能 (1-2个)
        num_skills = min(2, quality.value // 3 + 1)
        partner.skills = random.sample(PartnerSystem.SKILL_POOL, num_skills)
        
        # 随机功法
        partner.technique = random.choice(PartnerSystem.TECHNIQUE_POOL)
        
        # 高品质有额外属性
        if quality.value >= PartnerQuality.GOLDEN_CORE.value:
            partner.crit += 0.05
            partner.cultivation_boost += 0.1
        
        return partner
    
    @staticmethod
    def find_partner(
        player_partners: List[Partner], 
        player_realm: str,
        prefer_higher: bool = False
    ) -> Partner:
        """寻找仙侣"""
        realm_map = {
            "凡人": 1, "炼气期": 1, "筑基期": 2, "金丹期": 3,
            "元婴期": 4, "化神期": 5, "合体期": 6, "大乘期": 7
        }
        realm_index = realm_map.get(player_realm, 1)
        
        if prefer_higher and realm_index > 1:
            realm_index += random.randint(0, 1)
        
        # 根据玩家境界决定遇到什么类型的仙侣
        type_roll = random.random()
        if realm_index >= 6:
            # 高境界可以遇到仙人和特殊种族
            partner_type = random.choice([
                PartnerType.IMMORTAL, PartnerType.DRAGON, 
                PartnerType.PHOENIX, PartnerType.SPIRIT
            ])
        elif realm_index >= 4:
            partner_type = random.choice([
                PartnerType.CULTIVATOR, PartnerType.SPIRIT, 
                PartnerType.GHOST
            ])
        elif realm_index >= 2:
            partner_type = random.choice([
                PartnerType.CULTIVATOR, PartnerType.DEMON
            ])
        else:
            partner_type = PartnerType.CULTIVATOR
        
        return PartnerSystem.generate_partner(partner_type, realm_index)
    
    @staticmethod
    def cultivate_together(
        player, 
        partner: Partner, 
        hours: float
    ) -> Dict:
        """双修"""
        if not partner.can_cultivate():
            return {"error": "仙侣当前状态无法双修"}
        
        if player.hp <= 0:
            return {"error": "你已受伤，无法双修"}
        
        partner.state = PartnerState.CULTIVATING
        
        # 基础修为获取
        base_cultivation = 15 * hours
        
        # 仙侣加成
        affection_bonus = 1.0 + (partner.affection / 100.0) * 0.5
        cultivation_bonus = 1.0 + partner.cultivation_boost
        
        # 命运纠缠加成
        fate_bonus = 1.0 + (partner.fate / 200.0)
        
        # 综合加成
        total_bonus = affection_bonus * cultivation_bonus * fate_bonus
        
        # 玩家获得修为
        player_cultivation = base_cultivation * total_bonus
        player.gain_cultivation(player_cultivation)
        
        # 仙侣获得修为 (略少)
        partner_cultivation = base_cultivation * total_bonus * 0.8
        
        # 属性随机提升
        attr_gains = []
        if random.random() < 0.15 * hours:
            player.attack += 1
            attr_gains.append("攻击+1")
        if random.random() < 0.1 * hours:
            player.defense += 1
            attr_gains.append("防御+1")
        
        # 仙侣好感度提升
        affection_change = random.randint(1, 3)
        affection_result = partner.update_affection(affection_change)
        
        # 命运纠缠提升
        fate_gain = random.randint(1, 2)
        partner.gain_fate(fate_gain)
        
        partner.last_cultivation += hours
        
        partner.state = PartnerState.IDLE
        
        return {
            "player_cultivation": player_cultivation,
            "partner_cultivation": partner_cultivation,
            "total_bonus": total_bonus,
            "attr_gains": attr_gains,
            "affection_change": affection_change,
            "affection_result": affection_result,
            "fate_gain": fate_gain,
            "message": f"双修 {hours} 小时，获得 {player_cultivation:.1f} 修为 (加成 {total_bonus:.2f}x)"
        }
    
    @staticmethod
    def give_gift(partner: Partner, gift_name: str = None) -> Dict:
        """赠送礼物"""
        if gift_name:
            # 查找指定礼物
            gift = None
            for g in PARTNER_GIFTS:
                if g.name == gift_name:
                    gift = g
                    break
            if not gift:
                return {"error": f"没有名为 {gift_name} 的礼物"}
        else:
            # 随机礼物
            gift = random.choice(PARTNER_GIFTS)
        
        # 更新好感度
        affection_result = partner.update_affection(gift.affection_gain)
        
        # 命运纠缠也可能增加
        fate_gain = random.randint(0, 1)
        if fate_gain > 0:
            partner.gain_fate(fate_gain)
        
        return {
            "gift": gift.name,
            "affection_gain": gift.affection_gain,
            "fate_gain": fate_gain,
            "new_affection": affection_result["new_affection"],
            "level_changed": affection_result["level_changed"],
            "new_level": affection_result.get("new_level", ""),
            "message": f"赠送 {gift.name}，好感度 +{gift.affection_gain}"
        }
    
    @staticmethod
    def joint_combat(
        player, 
        partners: List[Partner], 
        enemy_level: int
    ) -> Dict:
        """并肩作战"""
        # 筛选可战斗的仙侣
        battle_partners = [p for p in partners if p.hp > 0 and p.state == PartnerState.IDLE]
        
        if not battle_partners:
            return {"error": "没有可参战的仙侣"}
        
        # 敌人属性
        enemy_hp = 60 + enemy_level * 18
        enemy_attack = 4 + enemy_level * 2.5
        
        combat_log = []
        
        # 计算玩家和仙侣的总属性
        total_attack = player.attack
        total_defense = player.defense
        
        for partner in battle_partners:
            partner.state = PartnerState.COMBAT
            # 仙侣参战加成
            affection_bonus = 1.0 + (partner.affection / 200.0)
            total_attack += int(partner.attack * affection_bonus)
            total_defense += int(partner.defense * affection_bonus)
        
        combat_log.append(f"【并肩作战】你与 {len(battle_partners)} 位仙侣联手对敌")
        
        round_num = 0
        while player.hp > 0 and enemy_hp > 0:
            round_num += 1
            combat_log.append(f"\n--- 第{round_num}回合 ---")
            
            # 仙侣攻击
            for partner in battle_partners:
                if partner.hp <= 0:
                    continue
                
                affection_bonus = 1.0 + (partner.affection / 200.0)
                damage = int(partner.attack * affection_bonus)
                
                # 暴击
                is_crit = random.random() < partner.crit
                if is_crit:
                    damage = int(damage * 1.5)
                    combat_log.append(f"暴击! {partner.name}造成 {damage} 点伤害")
                else:
                    combat_log.append(f"{partner.name}造成 {damage} 点伤害")
                
                enemy_hp -= damage
            
            if enemy_hp <= 0:
                break
            
            # 玩家攻击
            player_damage = player.attack
            if random.random() < player.crit:
                player_damage = int(player_damage * 1.5)
                combat_log.append(f"你暴击造成 {player_damage} 点伤害")
            else:
                combat_log.append(f"你造成 {player_damage} 点伤害")
            enemy_hp -= player_damage
            
            if enemy_hp <= 0:
                break
            
            # 敌人攻击 (分摊)
            damage_per_target = enemy_attack // (len(battle_partners) + 1)
            
            # 玩家受伤
            actual = player.take_damage(damage_per_target)
            combat_log.append(f"敌人对你造成 {actual} 点伤害")
            
            # 仙侣受伤
            for partner in battle_partners:
                if partner.hp <= 0:
                    continue
                actual = partner.take_damage(damage_per_target)
                combat_log.append(f"敌人对{partner.name}造成 {actual} 点伤害")
        
        # 恢复仙侣状态
        for partner in battle_partners:
            partner.state = PartnerState.IDLE
        
        # 战斗结果
        if player.hp > 0:
            reward = enemy_level * 20 + 40
            
            # 仙侣获得好感度
            for partner in battle_partners:
                affection_gain = random.randint(2, 5)
                partner.update_affection(affection_gain)
            
            # 命运纠缠提升
            for partner in battle_partners:
                if random.random() < 0.3:
                    partner.gain_fate(2)
            
            return {
                "win": True,
                "reward": reward,
                "log": combat_log,
                "affection_gains": {p.name: 3 for p in battle_partners}
            }
        else:
            # 失败扣好感
            for partner in battle_partners:
                partner.update_affection(-3)
            
            return {
                "win": False,
                "log": combat_log
            }
    
    @staticmethod
    def visit_partner(partner: Partner) -> str:
        """探访仙侣"""
        affection = partner.get_affection_level()
        
        messages = []
        
        if affection == AffectionLevel.SOULMATE:
            messages = [
                "你们相对而坐，默契地开始了今天的修炼",
                "无需言语，你们心意相通，灵气自然流转",
                "携手漫步云端，享受这难得的宁静时光"
            ]
        elif affection == AffectionLevel.BELOVED:
            messages = [
                "仙侣见到你非常高兴，脸上洋溢着幸福的笑容",
                "你们相视一笑，开始了双修",
                "仙侣轻声为你整理衣襟，温柔备至"
            ]
        elif affection == AffectionLevel.CLOSE:
            messages = [
                "仙侣热情地招待你，分享最近的趣事",
                "你们讨论道法，互相印证",
                "仙侣为你准备了灵茶和点心"
            ]
        elif affection == AffectionLevel.FRIEND:
            messages = [
                "仙侣礼貌地迎接你，你们交流修炼心得",
                "你们互相分享最近的经历",
                "仙侣向你点头致意"
            ]
        elif affection == AffectionLevel.ACQUAINTANCE:
            messages = [
                "仙侣对你有些拘谨，但仍然礼貌相待",
                "你们简单地交谈了几句",
                "仙侣保持着适当的距离"
            ]
        else:
            messages = [
                "仙侣对你态度冷淡",
                "仙侣转身离去，不愿多言",
                "气氛有些尴尬"
            ]
        
        return random.choice(messages)
    
    @staticmethod
    def break_bond(partner: Partner) -> str:
        """解除道侣关系"""
        return f"你与 {partner.name} 的道侣关系已解除，各自天涯"
    
    @staticmethod
    def get_partner_summary(partners: List[Partner]) -> str:
        """获取仙侣概览"""
        if not partners:
            return "暂无仙侣"
        
        lines = ["【仙侣道侣】"]
        for i, p in enumerate(partners, 1):
            affection = p.get_affection_level()
            lines.append(f"{i}. {p.name} ({p.get_type_name()}) - {p.realm}第{p.level}层")
            lines.append(f"   好感: {p.affection}% ({affection.value}) | 命运: {p.fate}%")
        
        return "\n".join(lines)
    
    @staticmethod
    def get_combined_cultivation_boost(partners: List[Partner]) -> float:
        """获取所有仙侣的总双修加成"""
        total = 0.0
        for p in partners:
            if p.state == PartnerState.CULTIVATING:
                total += p.cultivation_boost
        return total
    
    @staticmethod
    def get_affection_reward(affection: int) -> Dict:
        """根据好感度获取约会奖励"""
        reward_multiplier = 1.0 + (affection / 50.0)
        
        return {
            "cultivation_bonus": reward_multiplier,
            "gift_bonus": 1 + (affection // 20) * 0.2,
            "combat_bonus": 1 + (affection // 25) * 0.15
        }
