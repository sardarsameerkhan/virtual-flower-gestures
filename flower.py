import cv2
import math

class InstagramFlower:
    def __init__(self):
        self.wx = 0  
        self.wy = 0  
        self.tip_x = 0
        self.tip_y = 0
        self.max_stem_length = 220  # Slightly longer stems for better separation
        
        # Load only the two requested assets
        self.asset_mid = cv2.imread('assets/mid.png', cv2.IMREAD_UNCHANGED)
        self.asset_full = cv2.imread('assets/full.png', cv2.IMREAD_UNCHANGED)
        
        # Sub-branch angle configurations (offsets in radians)
        # This splits 1 main stem into 3 distinct sub-stems
        self.branch_offsets = [-0.18, 0.0, 0.18] 

    def update_bouquet_position(self, wrist_x, wrist_y, tip_x, tip_y, growth_progress):
        """Saves core coordinates to compute the sub-branches during rendering."""
        self.wx = wrist_x
        self.wy = wrist_y
        self.tip_x = tip_x
        self.tip_y = tip_y

    def get_sub_branch_endpoints(self, idx, growth_progress):
        """Calculates unique endpoints for 3 sub-stems per finger branch."""
        dx = self.tip_x - self.wx
        dy = self.tip_y - self.wy
        
        base_angle = math.atan2(dy, dx)
        magnitude = math.hypot(dx, dy) * 1.3  # Extend outward beyond the fingertip
        
        # Apply the unique angle offset for this sub-branch
        final_angle = base_angle + self.branch_offsets[idx]
        
        target_head_x = self.wx + magnitude * math.cos(final_angle)
        target_head_y = self.wy + magnitude * math.sin(final_angle)
        
        # Linearly interpolate based on growth progress
        hx = int(self.wx + (target_head_x - self.wx) * growth_progress)
        hy = int(self.wy + (target_head_y - self.wy) * growth_progress)
        return hx, hy

    def overlay_png(self, background, overlay, cx, cy, size):
        """Blends transparent PNG alpha-channels smoothly over the video matrix."""
        if overlay is None or size <= 0:
            return background
            
        img = cv2.resize(overlay, (size, size), interpolation=cv2.INTER_AREA)
        x1, x2 = cx - size // 2, cx + size // 2
        y1, y2 = cy - size // 2, cy + size // 2
        
        h, w, _ = background.shape
        if x1 < 0 or y1 < 0 or x2 > w or y2 > h:
            return background

        overlay_color = img[:, :, :3]
        mask = img[:, :, 3] / 255.0
        
        for c in range(0, 3):
            background[y1:y2, x1:x2, c] = (
                background[y1:y2, x1:x2, c] * (1.0 - mask) + 
                overlay_color[:, :, c] * mask
            )
        return background

    def draw_all_branches(self, frame, growth_progress):
        """Draws all 3 interconnected sub-stems originating from the wrist base."""
        if growth_progress <= 0.05:
            return
            
        for i in range(3):
            hx, hy = self.get_sub_branch_endpoints(i, growth_progress)
            # Dual-line drawing to emulate a glowing neon vector asset
            cv2.line(frame, (self.wx, self.wy), (hx, hy), (255, 185, 80), 2, cv2.LINE_AA)
            cv2.line(frame, (self.wx, self.wy), (hx, hy), (255, 235, 170), 1, cv2.LINE_AA)

    def draw_all_flowers(self, frame, growth_progress, bloom_progress):
        """Spawns highly detailed flower assets on top of every sub-branch tip."""
        if growth_progress > 0.4 and bloom_progress > 0.05:
            # High scale factor (130px) ensures petals overlap into a dense cluster
            flower_size = int(130 * bloom_progress)
            if flower_size % 2 != 0: 
                flower_size += 1 
            
            for i in range(3):
                hx, hy = self.get_sub_branch_endpoints(i, growth_progress)
                
                # Bud image is removed! Transitions exclusively between mid and full bloom
                if bloom_progress < 0.65:
                    frame = self.overlay_png(frame, self.asset_mid, hx, hy, flower_size)
                else:
                    frame = self.overlay_png(frame, self.asset_full, hx, hy, flower_size)