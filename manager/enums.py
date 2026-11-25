from enum import Enum


class PositionTypeEnum(Enum):
    DEVELOPER = "Developer"
    MANAGER = "Project Manager"
    QA = "QA"
    DESIGNER = "Designer"
    DEVOPS = "DevOps"


class TaskTypeEnum(Enum):
    BUG = "Bug"
    FEATURE = "Feature"
    BREAKING_CHANGE = "Breaking Change"
    REFACTORING = "Refactoring"
    QA = "QA"


class TaskStatusEnum(Enum):
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    QA = "QA"
    DONE = "Done"


class PriorityEnum(Enum):
    LOW = "Low"
    NORMAL = "Normal"
    HIGH = "High"
    URGENT = "Urgent"
