
def merge_pairs(list, should_merge, merge):
    """
    Merges adjacent elements of list using the function merge
    if they satisfy the predicate should_merge.

    >>> merge_pairs([], None, None)
    []

    >>> merge_pairs([1], None, None)
    [1]

    >>> merge_pairs([1, 2], lambda x, y: False, None)
    [1, 2]

    >>> merge_pairs([1, 2], lambda x, y: y == x + 1, lambda x, y: (x, y))
    [(1, 2)]

    >>> merge_pairs([1, 2, 3], lambda x, y: y == x + 1, lambda x, y: (x, y))
    [(1, 2), 3]

    >>> merge_pairs([1, 2, 3, 4], lambda x, y: y == x + 1, lambda x, y: (x, y))
    [(1, 2), (3, 4)]
    """
    ret = []
    i = 0
    while i < len(list) - 1:
        a = list[i]
        b = list[i + 1]
        if should_merge(a, b):
            ret.append(merge(a, b))
            i += 2
        else:
            ret.append(a)
            i += 1
    if i == len(list) - 1:
        ret.append(list[i])
    return ret
