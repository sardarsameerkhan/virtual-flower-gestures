import cv2
import math
import numpy as np

class InstagramFlower:
    def __init__(self):
        self.wx = 0  
        self.wy = 0  
        self.tip_x = 0
        self.tip_y = 0
        
        self.prev_hx = [None, None, None]
        self.prev_hy = [None, None, None]
        
        # Load only the single asset in its true colors
        self.asset_full = cv2.imread('assets/full.png', cv2.IMREAD_UNCHANGED)
        
        # Cache variables to maintain 30+ FPS
        self.cached_size = -1
        self.cached_img = None
        self.cached_mask = None
        self.cached_color = None
        
        self.branch_offsets = [-0.18, 0.0, 0.18] 

    def update_bouquet_position(self, wrist_x, wrist_y, tip_x, tip_y, growth_progress):
        self.wx = wrist_x
        self.wy = wrist_y
        self.tip_x = tip_x
        self.tip_y = tip_y

    def get_sub_branch_endpoints(self, idx, growth_progress):
        dx = self.tip_x - self.wx
        dy = self.tip_y - self.wy
        base_angle = math.atan2(dy, dx)
        magnitude = math.hypot(dx, dy) * 1.35  
        
        final_angle = base_angle + self.branch_offsets[idx]
        target_head_x = self.wx + magnitude * math.cos(final_angle)
        target_head_y = self.wy + magnitude * math.sin(final_angle)
        
        ideal_hx = int(self.wx + (target_head_x - self.wx) * growth_progress)
        ideal_hy = int(self.wy + (target_head_y - self.wy) * growth_progress)
        
        if self.prev_hx[idx] is None:
            self.prev_hx[idx] = ideal_hx
            self.prev_hy[idx] = ideal_hy
        else:
            self.prev_hx[idx] = int(self.prev_hx[idx] + 0.15 * (ideal_hx - self.prev_hx[idx]))
            self.prev_hy[idx] = int(self.prev_hy[idx] + 0.15 * (ideal_hy - self.prev_hy[idx]))
            
        return self.prev_hx[idx], self.prev_hy[idx]

    def draw_curved_gradient_stem(self, frame, start_pt, end_pt, idx, growth_progress):
        if growth_progress <= 0.05:
            return

        mid_x = (start_pt[0] + end_pt[0]) / 2
        mid_y = (start_pt[1] + end_pt[1]) / 2
        dx = end_pt[0] - start_pt[0]
        dy = end_pt[1] - start_pt[1]
        
        perp_x = -dy * (self.branch_offsets[idx] * 0.6)
        perp_y = dx * (self.branch_offsets[idx] * 0.6)
        ctrl_x = int(mid_x + perp_x)
        ctrl_y = int(mid_y + perp_y)

        steps = 16
        curve_pts = []
        for step in range(steps + 1):
            t = step / steps
            x = (1-t)**2 * start_pt[0] + 2*(1-t)*t * ctrl_x + t**2 * end_pt[0]
            y = (1-t)**2 * start_pt[1] + 2*(1-t)*t * ctrl_y + t**2 * end_pt[1]
            curve_pts.append((int(x), int(y)))

        for i in range(len(curve_pts) - 1):
            t = i / steps
            b = int((1 - t) * 120 + t * 240)
            g = int((1 - t) * 40 + t * 220)
            r = int((1 - t) * 160 + t * 60)
            
            cv2.line(frame, curve_pts[i], curve_pts[i+1], (b, g, r), 3, cv2.LINE_AA)
            cv2.line(frame, curve_pts[i], curve_pts[i+1], (255, 255, 255), 1, cv2.LINE_AA)

    def overlay_png_fast(self, background, cx, cy, size):
        """Blends the raw flower image rapidly without any color shifting alterations."""
        if size <= 0 or self.asset_full is None:
            return background

        # Performance booster: Recalculate cache only if image size scales up/down
        if size != self.cached_size:
            resized = cv2.resize(self.asset_full, (size, size), interpolation=cv2.INTER_LINEAR)
            self.cached_size = size
            self.cached_color = resized[:, :, :3]
            self.cached_mask = (resized[:, :, 3] / 255.0)[:, :, np.newaxis]
        
        x1, x2 = cx - size // 2, cx + size // 2
        y1, y2 = cy - size // 2, cy + size // 2
        
        h, w, _ = background.shape
        if x1 < 0 or y1 < 0 or x2 > w or y2 > h:
            return background

        roi = background[y1:y2, x1:x2]
        background[y1:y2, x1:x2] = (roi * (1.0 - self.cached_mask) + self.cached_color * self.cached_mask).astype(np.uint8)
        return background

    def draw_all_branches(self, frame, growth_progress):
        if growth_progress <= 0.05:
            self.prev_hx = [None, None, None]
            self.prev_hy = [None, None, None]
            return
            
        for i in range(3):
            hx, hy = self.get_sub_branch_endpoints(i, growth_progress)
            self.draw_curved_gradient_stem(frame, (self.wx, self.wy), (hx, hy), i, growth_progress)

    def draw_all_flowers(self, frame, growth_progress, bloom_progress):
        if growth_progress > 0.4 and bloom_progress > 0.05:
            flower_size = int(140 * bloom_progress)
            if flower_size % 2 != 0: 
                flower_size += 1 
            
            for i in range(3):
                hx, hy = self.get_sub_branch_endpoints(i, growth_progress)
                frame = self.overlay_png_fast(frame, hx, hy, flower_size)