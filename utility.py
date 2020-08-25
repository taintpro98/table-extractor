import cv2
from utils import sort_layout_output

def location2bbox(location):
    xmin = min(p[0] for p in location)
    xmax = min(p[0] for p in location)
    ymin = min(p[1] for p in location)
    ymax = min(p[1] for p in location)
    return [int(xmin), int(ymin), int(xmax), int(ymax)]

def visualize_layout(result, image):
    if result is None:
        return image
    color = (255, 0, 0) 
    thickness = 2
    for r in result:
        location = r['location']
        tlbr_poses = (location2bbox(location))
        image = cv2.rectangle(image, tlbr_poses[:2], tlbr_poses[2:], color, thickness) 
    return image

def visualize_table(refined_boxes, image):
    if refined_boxes is None:
        return image
    color = (0, 255, 0) 
    thickness = 2
    for r in refined_boxes:
        location = r['location']
        tlbr_poses = (location2bbox(location))
        image = cv2.rectangle(image, tlbr_poses[:2], tlbr_poses[2:], color, thickness) 
    return image

def check_layout_in_cell(lay, ce, threshold=0.5):
    layloc = lay['location']
    celoc = ce['location']
    (xlay0, ylay0), (_,_), (xlay1, ylay1), (_,_) = layloc
    x0 = max(xlay0, celoc[0][0])
    y0 = max(ylay0, celoc[0][1])
    x1 = min(xlay1, celoc[2][0])
    y1 = min(ylay1, celoc[2][1])
    if x1 <= x0 or y1 <= y0:
        return False
    intersection = (x1 - x0) * (y1 - y0)
    area = (xlay1 - xlay0) * (ylay1 - ylay0) # area of layout
    iou = intersection/float(area)
    return (iou > threshold)

def define_containers(layout_output, cells):
    for lay in layout_output:
        for idx, ce in enumerate(cells):
            if check_layout_in_cell(lay, ce):
                lay['belong'] = idx
                break
        if lay.get('belong', None) is None:
            lay['belong'] = 0 # None
    return layout_output

def is_available_merged(lay1, lay2, threshold=0.2):
    if lay1['belong'] != lay2['belong'] or lay1['line'] != lay2['line']:
        return False
    (x0, y0), (_,_), (x1, y1), (_,_) = lay1['location']
    (a0, b0), (_,_), (a1, b1), (_,_) = lay2['location']
    distance = a0 - x1
    if distance <= 0:
        return True
    union_dis = a1 - x0
    if distance/float(union_dis) < threshold:
        return True
    return False

def merge_layouts(layout_output):
    res = []
    pivot = 0
    for idx, lay in enumerate(layout_output):
        if idx < len(layout_output) - 1:
            if not is_available_merged(lay, layout_output[idx+1]):
                x0, y0 = layout_output[pivot]['location'][0]
                x1, y1 = lay['location'][2]
                merged_layout = {
                    'bbox': [x0, y0, x1, y1],
                    'line': lay['line'],
                    'belong': lay['belong']
                }
                res.append(merged_layout)
                pivot = idx+1
    return res

def is_same_col(lay1, lay2, threshold=0.2):
    x0, _, x1, _ = lay1['bbox']
    a0, _, a1, _ = lay2['bbox']
    lay_min = min(x1 - x0, a1 - a0)
    xu0 = min(x0, a0)
    xu1 = max(x1, a1)
    xi0 = max(x0, a0)
    xi1 = min(x1, a1)
    rate = (xi1 - xi0) / float(lay_min)
    if rate > threshold:
        return True
    return False

def classify_cols(layout_output):
#     idxt = 0
    for idxt, lay in enumerate(layout_output):
        if lay['line'] != 0:
            break
    if len(layout_output) == 0:
        return []
    layout_output[idxt]['col_lead'] = idxt
    leaders = [] # leader of colums
    leaders.append(idxt)   
    for idx, lay in enumerate(layout_output[idxt+1:]):
        for i in range(idxt, idxt + idx + 1):
            if is_same_col(lay, layout_output[i]):
                lay['col_lead'] = layout_output[i]['col_lead']
                break
        if lay.get('col_lead', None) is None:
            lay['col_lead'] = idx + idxt + 1
            leaders.append(idx + idxt + 1)
    return leaders

def combine_cols(layout_output, leaders):
    idxt = leaders[0]
    for lay1 in layout_output[idxt:]:
        for lay2 in layout_output[idxt:]:
            if lay1['col_lead'] != lay2['col_lead']:
                if is_same_col(lay1, lay2):
                    true_leader = min(lay1['col_lead'], lay2['col_lead'])
                    fake_leader = max(lay1['col_lead'], lay2['col_lead'])
                    lay1['col_lead'] = true_leader
                    lay1['col_lead'] = true_leader
                    if fake_leader in leaders:
                        leaders.remove(fake_leader)

def define_col_cluster(leaders, layout_output):
    idxt = leaders[0]
    def criteria(idx):
        return layout_output[idx]['bbox'][0]
    leaders.sort(key=criteria)
    for i, lay in enumerate(layout_output[idxt:]):
        lay['col'] = leaders.index(lay['col_lead'])

def cells_same_col(c1, c2, threshold=0.8):
    location1 = c1['location']
    location2 = c2['location']
    tlbr_poses_1 = (location2bbox(location1))
    tlbr_poses_2 = (location2bbox(location2))
    xi0 = max(tlbr_poses_1[0], tlbr_poses_2[0])
    xi1 = min(tlbr_poses_1[2], tlbr_poses_2[2])
    if xi0 >= xi1:
        return False
    rate = (xi1 - xi0)/float(tlbr_poses_1[2] - tlbr_poses_1[0])
    if rate < threshold:
        return False
    return True

def define_headers(layout_output, leaders, cells):
    headers = []
    leaders_clone = leaders.copy()
    for idx, h in enumerate(layout_output):
        if h['line'] == 0:
            c1 = cells[h.get('belong', 0)]
            head = [] # set of cols belonging to this header
            for l in leaders:
                c2 = cells[layout_output[l]['belong']]
                if cells_same_col(c1, c2) and l in leaders_clone:
                    head.append(l)
                    leaders_clone.remove(l)
            headers.append(head)

    tmp = 0
    for idx, head in enumerate(headers):
        n = len(head)
        if n == 0:
            layout_output[idx]['col'] = [tmp, tmp]
            tmp += 1
            continue
        for jdx, lead in enumerate(head):
            layout_output[lead]['col'] = tmp + jdx 
        layout_output[idx]['col'] = [tmp, tmp + n - 1] 
        tmp += n
    
    for lay in layout_output:
        if lay['line'] != 0:
            lay['col'] = layout_output[lay['col_lead']]['col']

def locate_layouts(cells, layouts):
    layout_output = sort_layout_output(layouts) # sorted layout from left to right, top to down and define lines of layout
    layout_output = define_containers(layout_output, cells) # define which cell contains layout
    layout_output = merge_layouts(layout_output) # merge layouts besides each other
    leaders = classify_cols(layout_output) # classify layout into right columns
    combine_cols(layout_output, leaders) # combine columns that haven't been right
    define_col_cluster(leaders, layout_output) # define clusters into right colums
    define_headers(layout_output, leaders, cells) # place columns into right header
    return layout_output