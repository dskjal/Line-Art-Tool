[日本語](#日本語)

# Line Art Tool
Add line art shortcut in the tool tab in the sidebar. You can assign vertices in edit mode.  

Blender 2.93 or later is required.

# How to use
After setup line art with Add Line Art Grease Pencil, assign vertices to opacity or thickness.  

When you want to add some line art modifier for edge type or object, press 'Add Line Art Modifier.' You can select the active line art modifier by clicking the arrow icon on the far right. An active line art name is redded.  

Base {Opacity, Thickness, Color} change unassigned elements. Add {Opacity, Thickness, Color} add layer and manage multiple elements. You can change for each element names.

## Camera
Line art needs to be viewed from a camera. Lock button switches to camera view and lock camera to view.

### Line Offset
Line Offset prevents burying the lines in mesh, by offsetting the lines in the reverse view vector. That uses an Offset modifier.

## Layer
A bulb icon in a layer is the "Use Lights" option. Disable line lighting when the option is off.

## Line Thickness
Setting Stroke Thickness to Screen Space allows you to fix the line width.

# Color is not working
Switch viewport shading to material preview or render.

# The intersection line is not colored
The intersection line can not color. This is a Vertex Weight Transfer limitation.

# 日本語
サイドバーのツールにラインアートのショートカットを追加する。メッシュのエディットモードで各種の割り当てができる。  

対応バージョンは 2.93 以降。  

# 使い方 
Add Line Art Grease Pencil でラインアートを自動設定した後、不透明度や幅を割り当てる。  

エッジタイプやオブジェクトごとにラインアートモディフィアを分けたいときは、Add Line Art Modifier でラインアートモディフィアを追加できる。一番右端の矢印アイコンをクリックすることで、アクティブなラインアートモディフィアを選択できる。アクティブなラインアートは名前が赤くなる。  

Base {Opacity, Thickness, Color} は未割り当ての要素を変更する。Add {Opacity, Thickness, Color} でレイヤーを追加し、複数の要素を管理できる。要素の名前は自由に変更できる。 

## カメラ
ラインアートはカメラから見る必要がある。Lock はカメラビューに移行し、カメラをビューにロックする。  

### ラインオフセット 
ラインオフセットはオフセットモディフィアを使い、カメラの視線ベクトルの逆方向に線をずらすことで、線がメッシュに埋まるのを防ぐ。  

## レイヤー 
レイヤーの電球アイコンは「ライトを使用」オプション。これを OFF にすると線がライトの影響を受けなくなる。  

## 線の幅
ストローク幅をスクリーン空間にすると、線幅を固定できる。

# 色がつかない場合 
３Ｄビューのシェーディングをマテリアルプレビューかレンダーにする。  

# 交差線に色がつかない 
Vertex Weight Transfer の仕様で交差線に色がつかない。  
