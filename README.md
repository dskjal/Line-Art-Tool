# Line Art Tool
サイドバーのツールにラインアートのショートカットを追加する。エディットモードで各種の割り当てができる。  
Add line art shortcut in the tool tab in the sidebar. You can assign vertices in edit mode.  

対応バージョンは 2.93。  
Blender 2.93 is required.

# 使い方 How to use
Add Line Art Grease Pencil でラインアートを自動設定した後、不透明度や幅を割り当てる。  
After setup line art with Add Line Art Grease Pencil, assign vertices to opacity or thickness.  

エッジタイプやオブジェクトごとにラインアートモディフィアを分けたいときは、Add Line Art Modifier でラインアートモディフィアを追加できる。一番右端の矢印アイコンをクリックすることで、アクティブなラインアートモディフィアを選択できる。アクティブなラインアートは名前が赤くなる。  
When you want to add some line art modifier for edge type or object, press 'Add Line Art Modifier.' You can select the active line art modifier by clicking the arrow icon on the far right. An active line art name is redded.  

Base {Opacity, Thickness, Color} は未割り当ての要素を変更する。Add {Opacity, Thickness, Color} でレイヤーを追加し、複数の要素を管理できる。要素の名前は自由に変更できる。  
Base {Opacity, Thickness, Color} change unassigned elements. Add {Opacity, Thickness, Color} add layer and manage multiple elements. You can change for each element names.

## カメラ Camera
ラインアートはカメラから見る必要がある。Lock はカメラビューに移行し、カメラをビューにロックする。  
Line art needs to be viewed from a camera. Lock button switches to camera view and lock camera to view.

## レイヤー Layer
レイヤーの電球アイコンは「ライトを使用」オプション。これを OFF にすると線がライトの影響を受けなくなる。  
A bulb icon in a layer is the "Use Lights" option. Disable line lighting when the option is off.

# 色がつかない場合 Color is not working
３Ｄビューのシェーディングをマテリアルプレビューかレンダーにする。  
Switch viewport shading to material preview or render.

# 交差線に色がつかない The intersection line is not colored
Vertex Weight Transfer の仕様で交差線に色がつかない。  
The intersection line can not color. This is a Vertex Weight Transfer limitation.
