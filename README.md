# Line Art Tool
サイドバーのツールにラインアートのショートカットを追加する。エディットモードで各種の割り当てができる。  
Add line art shortcut in the tool tab in the sidebar. You can assign vertices in edit mode.  

対応バージョンは 2.93。  
Blender 2.93 is required.

# 使い方 How to use
Add Line Art Grease Pencil でラインアートを自動設定した後、不透明度や幅を割り当てる。  
After setup line art with Add Line Art Grease Pencil, assign vertices to opacity or thickness.  

Base {Opacity, Thickness, Color} は未割り当ての要素を変更する。Add {Opacity, Thickness, Color} でレイヤーを追加し、複数の要素を管理できる。要素の名前は自由に変更できる。  
Base {Opacity, Thickness, Color} change unassigned elements. Add {Opacity, Thickness, Color} add layer and manage multiple elements. You can change for each element names.

## カメラ Camera
ラインアートはカメラから見る必要がある。Lock はカメラビューに移行し、カメラをビューにロックする。  
Line art needs to be viewed from a camera. Lock button switches to camera view and lock camera to view.

# 色がつかない場合 Color is not working
３Ｄビューのシェーディングをマテリアルプレビューかレンダーにする。  
Switch viewport shading to material preview or render.

# 交差線に色がつかない The intersection line is not colored
Vertex Weight Transfer の仕様で交差線に色はつけられません。  
The intersection line can not color. This is a Vertex Weight Transfer limitation.
