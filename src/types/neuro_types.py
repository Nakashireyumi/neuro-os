"""
Type definitions for Neuro-OS integration system
Defines all data structures for regionalization, context, and plugin architecture
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol, Union, Callable
from abc import ABC, abstractmethod

# === Core Enums ===

class RegionType(Enum):
    """Types of screen regions"""
    WINDOW = "window"
    BUTTON = "button"
    INPUT_FIELD = "input_field"
    TEXT_AREA = "text_area"
    MENU = "menu"
    TOOLBAR = "toolbar"
    TAB = "tab"
    DIALOG = "dialog"
    CONTENT_AREA = "content_area"
    IMAGE = "image"
    LINK = "link"
    ICON = "icon"
    LIST_ITEM = "list_item"
    CHECKBOX = "checkbox"
    RADIO_BUTTON = "radio_button"
    DROPDOWN = "dropdown"
    SLIDER = "slider"
    PROGRESS_BAR = "progress_bar"
    NOTIFICATION = "notification"
    UNKNOWN = "unknown"

class ContextType(Enum):
    """Types of context data"""
    VISUAL = "visual"
    INTERACTIVE = "interactive"
    APPLICATION = "application"
    USER_INTENT = "user_intent"
    TEMPORAL = "temporal"
    SYSTEM_STATE = "system_state"

class Priority(Enum):
    """Priority levels for context and actions"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class PluginType(Enum):
    """Types of plugins in the system"""
    REGION_DETECTOR = "region_detector"
    CONTEXT_PROVIDER = "context_provider"
    ACTION_HANDLER = "action_handler"
    APP_INTEGRATION = "app_integration"

# === Core Data Structures ===

@dataclass
class Coordinates:
    """Screen coordinates"""
    x: int
    y: int

    def __post_init__(self):
        """Validate coordinates - allow negative for multi-monitor setups"""
        if not isinstance(self.x, int) or not isinstance(self.y, int):
            raise ValueError("Coordinates must be integers")

@dataclass
class BoundingBox:
    """Rectangular bounding box with validation"""
    x: int
    y: int
    width: int
    height: int

    def __post_init__(self):
        """Validate bounding box"""
        if not all(isinstance(val, int) for val in [self.x, self.y, self.width, self.height]):
            raise ValueError("All bounding box values must be integers")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Width and height must be positive")

    @property
    def center(self) -> Coordinates:
        """Get center point of the bounding box"""
        return Coordinates(self.x + self.width // 2, self.y + self.height // 2)

    @property
    def area(self) -> int:
        """Get area of the bounding box"""
        return self.width * self.height

    def contains(self, point: Coordinates) -> bool:
        """Check if point is within bounding box"""
        return (self.x <= point.x <= self.x + self.width and 
                self.y <= point.y <= self.y + self.height)

    def overlaps(self, other: 'BoundingBox') -> bool:
        """Check if this box overlaps with another"""
        return not (self.x + self.width < other.x or 
                   other.x + other.width < self.x or
                   self.y + self.height < other.y or 
                   other.y + other.height < self.y)

@dataclass
class ScreenRegion:
    """Represents a region on the screen"""
    id: str
    region_type: RegionType
    bounds: BoundingBox
    confidence: float
    title: Optional[str] = None
    application: Optional[str] = None
    clickable: bool = False
    focusable: bool = False
    visible: bool = True
    enabled: bool = True
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate screen region"""
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")

@dataclass
class ContextData:
    """Context information extracted from the system"""
    context_type: ContextType
    timestamp: datetime
    data: Dict[str, Any]
    confidence: float
    source: str
    priority: Priority = Priority.MEDIUM
    expires_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate context data"""
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")

@dataclass
class NeuroAction:
    """Action that can be performed by Neuro"""
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    target_region: Optional[ScreenRegion] = None
    estimated_duration: float = 1.0
    requires_confirmation: bool = False
    reversible: bool = True
    
    def __post_init__(self):
        """Validate action"""
        if self.estimated_duration < 0:
            raise ValueError("Estimated duration cannot be negative")

@dataclass
class SystemState:
    """Current state of the system"""
    active_application: Optional[str]
    focused_region: Optional[ScreenRegion]
    all_regions: List[ScreenRegion]
    context_data: List[ContextData]
    available_actions: List[NeuroAction]
    timestamp: datetime
    screen_resolution: Optional[Coordinates] = None
    mouse_position: Optional[Coordinates] = None

# === Plugin Architecture ===

class RegionDetectorProtocol(Protocol):
    """Protocol for region detector plugins"""
    
    async def detect_regions(self, screenshot: bytes, context: Dict[str, Any]) -> List[ScreenRegion]:
        """Detect regions in a screenshot"""
        ...
    
    def get_supported_apps(self) -> List[str]:
        """Get list of supported applications"""
        ...

class ContextProviderProtocol(Protocol):
    """Protocol for context provider plugins"""
    
    async def extract_context(self, regions: List[ScreenRegion], app_name: str) -> List[ContextData]:
        """Extract context from regions and application"""
        ...
    
    def get_context_types(self) -> List[ContextType]:
        """Get supported context types"""
        ...

class ActionHandlerProtocol(Protocol):
    """Protocol for action handler plugins"""
    
    async def execute_action(self, action: NeuroAction) -> bool:
        """Execute an action"""
        ...
    
    def get_supported_actions(self) -> List[str]:
        """Get list of supported action names"""
        ...

class AppIntegrationProtocol(Protocol):
    """Protocol for application integration plugins"""
    
    async def get_app_context(self, app_name: str) -> List[ContextData]:
        """Get application-specific context"""
        ...
    
    async def get_app_actions(self, app_name: str) -> List[NeuroAction]:
        """Get application-specific actions"""
        ...
    
    def get_supported_apps(self) -> List[str]:
        """Get supported applications"""
        ...

@dataclass
class PluginMetadata:
    """Metadata for plugins"""
    name: str
    version: str
    author: str
    description: str
    plugin_type: PluginType
    supported_apps: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    enabled: bool = True

class PluginRegistry:
    """Registry for managing plugins"""
    
    def __init__(self):
        self.plugins: Dict[str, Any] = {}
        self.metadata: Dict[str, PluginMetadata] = {}
    
    def register_plugin(self, plugin: Any, metadata: PluginMetadata):
        """Register a plugin"""
        self.plugins[metadata.name] = plugin
        self.metadata[metadata.name] = metadata
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[Any]:
        """Get all plugins of a specific type"""
        return [
            plugin for name, plugin in self.plugins.items()
            if self.metadata[name].plugin_type == plugin_type and self.metadata[name].enabled
        ]
    
    def get_plugins_for_app(self, app_name: str) -> List[Any]:
        """Get all plugins that support a specific application"""
        return [
            plugin for name, plugin in self.plugins.items()
            if app_name in self.metadata[name].supported_apps and self.metadata[name].enabled
        ]

# === Message Building ===

class NeuroMessageBuilder:
    """Builds formatted messages for Neuro"""
    
    def __init__(self):
        self.current_state: Optional[SystemState] = None
    
    def update_state(self, state: SystemState):
        """Update the current system state"""
        self.current_state = state
    
    def build_context_message(self) -> str:
        """Build a context message for Neuro"""
        if not self.current_state:
            return "No system state available"
        
        state = self.current_state
        
        # Build message sections
        sections = []
        
        # Application info
        if state.active_application:
            sections.append(f"Active Application: {state.active_application}")
        
        # Region summary
        if state.all_regions:
            region_types = {}
            for region in state.all_regions:
                region_types[region.region_type.value] = region_types.get(region.region_type.value, 0) + 1
            
            sections.append(f"Screen Regions ({len(state.all_regions)} total):")
            for region_type, count in region_types.items():
                sections.append(f"  - {region_type}: {count}")
        
        # Focused element
        if state.focused_region:
            sections.append(f"Focused: {state.focused_region.title} ({state.focused_region.region_type.value})")
        
        # Available actions
        if state.available_actions:
            sections.append(f"Available Actions ({len(state.available_actions)}):")
            for action in state.available_actions[:5]:  # Show first 5
                sections.append(f"  - {action.name}: {action.description}")
            
            if len(state.available_actions) > 5:
                sections.append(f"  ... and {len(state.available_actions) - 5} more")
        
        # Context data summary
        if state.context_data:
            context_types = {}
            for context in state.context_data:
                context_types[context.context_type.value] = context_types.get(context.context_type.value, 0) + 1
            
            sections.append(f"Context Data:")
            for context_type, count in context_types.items():
                sections.append(f"  - {context_type}: {count} items")
        
        return "\n".join(sections)
    
    def build_action_response(self, action: NeuroAction, success: bool, details: str = "") -> str:
        """Build a response message after executing an action"""
        status = "successfully" if success else "failed to"
        message = f"Action '{action.name}' {status} executed"
        
        if details:
            message += f": {details}"
        
        return message
    
    def build_region_info(self, region: ScreenRegion) -> str:
        """Build detailed information about a specific region"""
        info = [
            f"Region: {region.title or 'Untitled'} ({region.region_type.value})",
            f"Bounds: {region.bounds.x},{region.bounds.y} {region.bounds.width}x{region.bounds.height}",
            f"Confidence: {region.confidence:.2f}",
        ]
        
        if region.application:
            info.append(f"Application: {region.application}")
        
        attributes = []
        if region.clickable:
            attributes.append("clickable")
        if region.focusable:
            attributes.append("focusable")
        if not region.visible:
            attributes.append("hidden")
        if not region.enabled:
            attributes.append("disabled")
        
        if attributes:
            info.append(f"Attributes: {', '.join(attributes)}")
        
        return "\n".join(info)

# === Export all types ===

__all__ = [
    # Enums
    'RegionType', 'ContextType', 'Priority', 'PluginType',
    
    # Core data structures  
    'Coordinates', 'BoundingBox', 'ScreenRegion', 'ContextData', 
    'NeuroAction', 'SystemState',
    
    # Plugin architecture
    'RegionDetectorProtocol', 'ContextProviderProtocol', 
    'ActionHandlerProtocol', 'AppIntegrationProtocol',
    'PluginMetadata', 'PluginRegistry',
    
    # Message building
    'NeuroMessageBuilder'
]