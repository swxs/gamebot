from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: int
    y: int


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    width: int
    height: int

    @property
    def center(self) -> Point:
        return Point(self.x + self.width // 2, self.y + self.height // 2)


@dataclass(frozen=True)
class OcrHit:
    text: str
    rect: Rect


@dataclass(frozen=True)
class MatchResult:
    top_left: Point
    bottom_right: Point

    @property
    def center(self) -> Point:
        return Point(
            (self.top_left.x + self.bottom_right.x) // 2,
            (self.top_left.y + self.bottom_right.y) // 2,
        )
