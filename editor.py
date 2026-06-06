*** Begin Patch
*** Update File: editor.py
@@
-    def push_history(self):
-        self.history.append(copy.deepcopy(self.map))
-        if len(self.history) > 20: self.history.pop(0)
+    def push_history(self):
+        # Use deque-like behavior for history to avoid O(n) pop(0).
+        self.history.append(copy.deepcopy(self.map))
+        if len(self.history) > 20:
+            # pop oldest entry
+            del self.history[0]
@@
-    def flood_fill(self, start_x, start_y, target_val, fill_val):
-        if target_val == fill_val: return
-        q = [(start_x, start_y)]
-        while q:
-            x, y = q.pop(0)
-            if self.map[y][x] == target_val:
-                self.map[y][x] = fill_val
-                if x > 0: q.append((x-1, y))
-                if x < MAP_SIZE - 1: q.append((x+1, y))
-                if y > 0: q.append((x, y-1))
-                if y < MAP_SIZE - 1: q.append((x, y+1))
+    def flood_fill(self, start_x, start_y, target_val, fill_val):
+        if target_val == fill_val: return
+        # Use a deque to avoid inefficient list pop(0)
+        from collections import deque
+        q = deque()
+        q.append((start_x, start_y))
+        while q:
+            x, y = q.popleft()
+            if self.map[y][x] == target_val:
+                self.map[y][x] = fill_val
+                if x > 0: q.append((x-1, y))
+                if x < MAP_SIZE - 1: q.append((x+1, y))
+                if y > 0: q.append((x, y-1))
+                if y < MAP_SIZE - 1: q.append((x, y+1))
*** End Patch