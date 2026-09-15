"""Ground-contact traces in the original 481 x 809 concept coordinate system.

The photograph is style/layout evidence. Routes describe visible circulation;
asset persistence checks alone do not establish visual parity.
"""
# Join the main trail, then divide toward the blue shed, cottage doorstep and
# the passage between the cottage and the two planted beds.
PATHS=[
 ('entry',[(110,392),(151,374),(191,353),(213,343),(226,331)],96),
 ('shed',[(176,361),(163,368),(151,366),(143,360)],55),
 ('garden_passage',[(207,346),(230,354),(249,356),(274,346),(302,330),(327,316)],76),
]
FENCES=[[(330,397),(380,371),(432,342),(386,320),(346,308),(310,292)],
        [(144,312),(177,295),(208,282)]]
ANCHORS={'tower':(351,347),'main_bed':(306,373),'flower_bed':(386,349)}
SHED_YAW=0  # Front hatch faces the screen-right courtyard approach.
# Shrub/fern/grass group contacts, leaving distinct short-grass gaps and paths.
CLUSTERS=[(153,329,8),(188,310,8),(207,326,5),(265,327,7),
 (304,309,8),(325,301,7),(338,319,6),(378,310,8),
 (408,334,6),(401,358,6),(353,371,5),(337,387,5),
 (279,390,8),(257,386,7),(222,378,7),(154,373,6),
 (120,367,5),(168,345,5)]
