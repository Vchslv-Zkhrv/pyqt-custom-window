from dataclasses import dataclass

"""
module with modes managing CWindow working
"""


class CMode():
    """
    Main mode class
    """

    def __init__(self) -> None:
        raise DeprecationWarning("CMode static class cannot be instantiated")


class GestureResizeMode(CMode):
    """
    superclass for mode classes managing window reaction to resize gestures
    """


class Always(GestureResizeMode):
    """
    CWindow always applies the shadow geometry, ignoring the min and max size properties
    """


class Acceptable(GestureResizeMode):
    """
    CWindow.window_shadow ignores screen areas that violate the min and max size properties
    """


class ShrinkAsPossible(GestureResizeMode):
    """
    CWindow shrinks to the window_shadow geometry, but does not violate the min size poperty.
    Screen areas that bigger than CWindow max size ignored.
    """


class Never(GestureResizeMode):
    """
    CWindow don't use resize gestures
    """


@dataclass
class GestureResizeModes():
    """
    Main resize gestures settings
    """
    always = Always
    acceptable = Acceptable
    shrink_as_possible = ShrinkAsPossible
    never = Never


class ScreenOrientationMode(CMode):
    """
    superclass for mode classes managing window behavior on different screen orientations
    """


class NoDifference(ScreenOrientationMode):
    """
    CWindow use the same resize gestures both on landscape and portrait orientations.
    """


class UseSpecial(ScreenOrientationMode):
    """
    CWindow uses specific resize gestures for different screen orientations
    """


class IgnorePortait(ScreenOrientationMode):
    """
    CWindow disallows all resize gestures (except fullscreen gesture) on portait screen orientation
    """


@dataclass
class ScreenOrientationModes():
    """
    Resize gestures behavior on different portrait orientations
    """
    no_difference = NoDifference
    use_special = UseSpecial
    ignore_portrait = IgnorePortait


class SidesUsingMode(CMode):
    """
    superclass for mode classes managing the set of screen sides that can be used in resize gestures
    """


class Whole(SidesUsingMode):
    """
    CWindow uses all acceptable resize gestures except bottom gesture.
    (if UseSpecial property is used, right and left on portrait orientaion)
    """


class IgnoreCorners(SidesUsingMode):
    """
    whole, but CWindow does not use corner resize gestures
    """


class FullscreenOnly(SidesUsingMode):
    """
    CWindow uses only the fullscreen resize gesture (move to the top edge).
    If UseSpecial property is used, move to right or left edge gesture.
    """


@dataclass
class SideUsingModes():
    """
    Defines the set of available resize gestures
    """
    whole = Whole
    ignore_corners = IgnoreCorners
    fullscreen_only = FullscreenOnly
