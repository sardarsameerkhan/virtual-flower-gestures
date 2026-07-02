import cv2
import math
import numpy as np

class InstagramFlower:
    def __init__(self):
        self.wx = 0  
        self.wy = 0  
        self.tip_x = 0
        self.tip_y = 0
        self.max_stem_length = 220  
        
        self.prev_hx = [None, None, None]
        self.prev_hy = [None, None, None]
        
        # Load assets
        self.asset_mid = cv2.imread('assets/mid.png', cv2.IMREAD_UNCHANGED)
        self.asset_full = cv2.imread('assets/full.png', cv2.IMREAD_UNCHANGED)
        
        # Cache variables for optimization
        self.cached_size = -1
        self.cached_asset_type = None
        self.cached_bloom = -1.0
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
        magnitude = math.hypot(dx, dy) * 1.3  
        
        final_angle = base_angle + self.branch_offsets[idx]
        target_head_x = self.wx + magnitude * math.cos(final_angle)
        target_head_y = self.wy + magnitude * math.sin(final_angle)
        
        ideal_hx = int(self.wx + (target_head_x - self.wx) * growth_progress)
        ideal_hy = int(self.wy + (target_head_y - self.wy) * growth_progress)
        
        if self.prev_hx[idx] is None:
            self.prev_hx[idx] = ideal_hx
            self.prev_hy[idx] = ideal_hy
        else:
            self.prev_hx[idx] = int(self.prev_hx[idx] + 0.18 * (ideal_hx - self.prev_hx[idx]))
            self.prev_hy[idx] = int(self.prev_hy[idx] + 0.18 * (ideal_hy - self.prev_hy[idx]))
            
        return self.prev_hx[idx], self.prev_hy[idx]

    def overlay_png_fast(self, background, overlay_type, cx, cy, size, bloom_progress):
        if size <= 0:
            return background
            
        overlay = self.asset_mid if overlay_type == 'mid' else self.asset_full
        if overlay is None:
            return background

        # Performance booster: Recalculate color matrices only if type, size, or bloom changes
        if size != self.cached_size or overlay_type != self.cached_asset_type or abs(bloom_progress - self.cached_bloom) > 0.05:
            resized = cv2.resize(overlay, (size, size), interpolation=cv2.INTER_LINEAR)
            
            self.cached_size = size
            self.cached_asset_type = overlay_type
            self.cached_bloom = bloom_progress
            
            bgr_channels = resized[:, :, :3]
            self.cached_mask = (resized[:, :, 3] / 255.0)[:, :, np.newaxis]
            
            # 🌟 NEW FEATURE: DYNAMIC COLOR SHIFTING ENGINE (HSV Space Shift)
            hsv = cv2.cvtColor(bgr_channels, cv2.COLOR_BGR2HSV)
            # Dynamically shift Hue channel by a factor of your bloom scaling dial
            hue_shift = int(bloom_progress * 40) 
            hsv[:, :, 0] = (hsv[:, :, 0].astype(np.int32) + hue_shift) % 180
            # Boost Saturation as the flower opens up
            hsv[:, :, 1] = np.clip(hsv[:, :, 1].astype(np.int32) + 20, 0, 255)
            
            self.cached_color = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
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
            cv2.line(frame, (self.wx, self.wy), (hx, hy), (255, 185, 80), 2, cv2.LINE_AA)
            cv2.line(frame, (self.wx, self.wy), (hx, hy), (255, 235, 170), 1, cv2.LINE_AA)

    def draw_all_flowers(self, frame, growth_progress, bloom_progress):
        if growth_progress > 0.4 and bloom_progress > 0.05:
            flower_size = int(130 * bloom_progress)
            if flower_size % 2 != 0: 
                flower_size += 1 
            
            asset_type = 'mid' if bloom_progress < 0.65 else 'full'
            
            for i in range(3):
                hx, hy = self.get_sub_branch_endpoints(i, growth_progress)
                frame = self.overlay_png_fast(frame, asset_type, hx, hy, flower_size, bloom_progress)