from enum import Enum
import cv2
from djitellopy import Tello
import mediapipe as mp
import numpy as np

class TelloState(Enum):
    LAND = "land"
    TAKEOFF = "takeoff"
    UP = "up"
    OPEN ="open"
    LEFT = "left"
    RIGHT="right"
    GAL="GAL"
    FIN="FIN"
    # 必要に応じて他の状態を追加

class Tello_TEST():
    
    def __init__(self):
        self.index_finger_up_frames = 0  #人差し指が上にあるフレーム数を追跡する変数
        self.index_finger_down_frames = 0  #人差し指が下にあるフレーム数を追跡する変数
        self.index_finger_open_frames =0#手が開いているフレーム数を追跡する変数
        self.index_finger_left_frames =0#人差し指が左に向いているフレーム数を追跡する変数
        self.index_finger_right_frames =0#人差し指が右に向いているフレーム数を追跡する変数
        self.gal_finger_frames =0#ギャルぴ
        self.tello = Tello()
        # 現在の状態を設定
        self.current_state = TelloState.LAND
    
    def calculate_distance(self, landmark1, landmark2):
        # 2つのランドマーク間のユークリッド距離を計算します
        return np.sqrt((landmark1.x - landmark2.x)**2 + (landmark1.y - landmark2.y)**2)

    
    def is_finger_open(self, finger_base, finger_tip, threshold=0.1):
        distance = self.calculate_distance(finger_base, finger_tip)
        return distance > threshold

    def are_all_fingers_open(self, hand_landmarks):
        fingers = [(1, 4), (5, 8), (9, 12), (13, 16), (17, 20)]  # (根本, 先端)のペア
        return all(self.is_finger_open(hand_landmarks.landmark[base], hand_landmarks.landmark[tip]) for base, tip in fingers)
    
    def analyze_hand_landmarks(self, hand_landmarks):
        # ランドマークのインデックス
        THUMB_TIP = 4
        INDEX_FINGER_TIP = 8
        INDEX_FINGER_MCP = 5
        MIDDLE_FINGER_TIP = 12
        MIDDLE_FINGER_MCP = 9
        RING_FINGER_TIP = 16
        RING_FINGER_MCP = 13
        PINKY_TIP = 20
        PINKY_MCP = 17

        # 人差し指と親指が伸びていて、他の指が折りたたまれているかどうかを判断
        is_thumb_extended = hand_landmarks.landmark[THUMB_TIP].y < hand_landmarks.landmark[INDEX_FINGER_TIP].y
        is_index_finger_extended = hand_landmarks.landmark[INDEX_FINGER_TIP].x < hand_landmarks.landmark[INDEX_FINGER_MCP].x
        is_middle_finger_folded = hand_landmarks.landmark[MIDDLE_FINGER_MCP].x > hand_landmarks.landmark[INDEX_FINGER_TIP].x
        is_ring_finger_folded = hand_landmarks.landmark[RING_FINGER_MCP].x > hand_landmarks.landmark[INDEX_FINGER_TIP].x
        is_pinky_folded = hand_landmarks.landmark[PINKY_MCP].x > hand_landmarks.landmark[INDEX_FINGER_TIP].x

        is_index_finger_extended_left = hand_landmarks.landmark[INDEX_FINGER_TIP].x > hand_landmarks.landmark[INDEX_FINGER_MCP].x
        is_middle_finger_folded_left = hand_landmarks.landmark[MIDDLE_FINGER_MCP].x < hand_landmarks.landmark[INDEX_FINGER_TIP].x
        is_ring_finger_folded_left = hand_landmarks.landmark[RING_FINGER_MCP].x < hand_landmarks.landmark[INDEX_FINGER_TIP].x
        is_pinky_folded_left = hand_landmarks.landmark[PINKY_MCP].x < hand_landmarks.landmark[INDEX_FINGER_TIP].x


        # まず人差し指が親指より右か左かで判定を行う
        if hand_landmarks.landmark[INDEX_FINGER_TIP].x < hand_landmarks.landmark[THUMB_TIP].x:
            if is_thumb_extended:
                if is_index_finger_extended:
                    if is_middle_finger_folded and is_ring_finger_folded and is_pinky_folded:
                        print("Pointing to the right")
                        self.index_finger_right_frames += 1
                        return True
        else:
            if is_thumb_extended and is_index_finger_extended_left and is_middle_finger_folded_left and is_ring_finger_folded_left and is_pinky_folded_left:
                print("Pointing to the left")
                self.index_finger_left_frames += 1
                return True

        return False
    def analyze_peace_reverse(self, hand_landmarks):
        # ランドマークのインデックス
        THUMB_TIP = 4
        INDEX_FINGER_TIP = 8
        INDEX_FINGER_MCP = 5
        MIDDLE_FINGER_TIP = 12
        MIDDLE_FINGER_MCP = 9
        RING_FINGER_TIP = 16
        RING_FINGER_MCP = 13
        PINKY_TIP = 20
        PINKY_MCP = 17

        # 人差し指と中指が伸びていて、他の指が折りたたまれているかどうかを判断
        is_index_finger_extended =  hand_landmarks.landmark[INDEX_FINGER_TIP].y > hand_landmarks.landmark[INDEX_FINGER_MCP].y
        is_middle_finger_extended =  hand_landmarks.landmark[INDEX_FINGER_TIP].y > hand_landmarks.landmark[MIDDLE_FINGER_MCP].y
        is_ring_finger_folded = hand_landmarks.landmark[RING_FINGER_MCP].y > hand_landmarks.landmark[RING_FINGER_TIP].y
        is_pinky_folded = hand_landmarks.landmark[PINKY_MCP].y > hand_landmarks.landmark[PINKY_TIP].y

        is_thumb_extended = hand_landmarks.landmark[THUMB_TIP].y < hand_landmarks.landmark[INDEX_FINGER_TIP].y


        # まず人差し指が親指より右か左かで判定を行う
        if is_index_finger_extended and is_middle_finger_extended and is_ring_finger_folded and is_pinky_folded:
            return True

        return False
    

    def analyze_hand_landmarks_down(self, hand_landmarks):
        # ランドマークのインデックス
        THUMB_TIP = 4
        INDEX_FINGER_TIP = 8
        INDEX_FINGER_MCP = 5
        MIDDLE_FINGER_TIP = 12
        MIDDLE_FINGER_MCP = 9
        RING_FINGER_TIP = 16
        RING_FINGER_MCP = 13
        PINKY_TIP = 20
        PINKY_MCP = 17

        # 人差し指と親指が伸びていて(親指が人差し指より下)、他の指が折りたたまれているかどうかを判断
        is_thumb_extended = hand_landmarks.landmark[THUMB_TIP].y > hand_landmarks.landmark[INDEX_FINGER_TIP].y
        is_index_finger_extended = hand_landmarks.landmark[INDEX_FINGER_TIP].x < hand_landmarks.landmark[INDEX_FINGER_MCP].x
        is_middle_finger_folded = hand_landmarks.landmark[MIDDLE_FINGER_MCP].x > hand_landmarks.landmark[INDEX_FINGER_TIP].x
        is_ring_finger_folded = hand_landmarks.landmark[RING_FINGER_MCP].x > hand_landmarks.landmark[INDEX_FINGER_TIP].x
        is_pinky_folded = hand_landmarks.landmark[PINKY_MCP].x > hand_landmarks.landmark[INDEX_FINGER_TIP].x

        is_index_finger_extended_left = hand_landmarks.landmark[INDEX_FINGER_TIP].x > hand_landmarks.landmark[INDEX_FINGER_MCP].x
        is_middle_finger_folded_left = hand_landmarks.landmark[MIDDLE_FINGER_MCP].x < hand_landmarks.landmark[INDEX_FINGER_TIP].x
        is_ring_finger_folded_left = hand_landmarks.landmark[RING_FINGER_MCP].x < hand_landmarks.landmark[INDEX_FINGER_TIP].x
        is_pinky_folded_left = hand_landmarks.landmark[PINKY_MCP].x < hand_landmarks.landmark[INDEX_FINGER_TIP].x


        # まず人差し指が親指より右か左かで判定を行う
        if hand_landmarks.landmark[INDEX_FINGER_TIP].x < hand_landmarks.landmark[THUMB_TIP].x:
            if is_thumb_extended:
                if is_index_finger_extended:
                    if is_middle_finger_folded and is_ring_finger_folded and is_pinky_folded:
                        print("Pointing to the right")
                        self.index_finger_right_frames += 1
                        return True
        else:
            if is_thumb_extended and is_index_finger_extended_left and is_middle_finger_folded_left and is_ring_finger_folded_left and is_pinky_folded_left:
                print("Pointing to the left")
                self.index_finger_left_frames += 1
                return True

        return False
    

    def start(self):
           
        self.tello.connect()
        print("Battery percentage:", self.tello.get_battery())

        self.tello.streamon()
        #self.tello.takeoff()


        # 状態のチェック
        if self.current_state == TelloState.LAND:
            print("Tello is currently landed.")

        

        while True:
            
            frame = self.tello.get_frame_read().frame
            frame = cv2.resize(frame, (640, 480))       
            self.mp_camera(frame)
            #cv2.imshow("Tello Video Stream", frame)

            key = cv2.waitKey(1)
            if key == 27:  # ESCキーで終了
                self.tello.streamoff()
                break
            if self.current_state == TelloState.FIN:
                print("STOP")
                break

        cv2.destroyAllWindows()

    def mp_camera(self, image):
        mp_drawing = mp.solutions.drawing_utils
        mp_hands = mp.solutions.hands

        with mp_hands.Hands(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as hands:
            # 後で自分撮りビューを表示するために画像を水平方向に反転し、BGR画像をRGBに変換
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

            # パフォーマンスを向上させるために、オプションで、参照渡しのためにイメージを書き込み不可としてマーク
            image.flags.writeable = False
            results = hands.process(image)


            # 画像に手のアノテーションを描画
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    # 全ての指の先端のy座標を取得
                    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y
                    index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
                    middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y
                    ring_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y
                    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y
                    #先端の平均値
                    y_mean = (thumb_tip + index_finger_tip +middle_finger_tip+ ring_finger_tip+pinky_tip)/5
                    #平均と中指との距離を閾値とする
                    alpha = 0.009
                    thres = np.abs(middle_finger_tip- y_mean)
                    #平均との人差し指との距離が閾値より大きいとき，伸ばしていると定義
                    up = np.abs(index_finger_tip-y_mean)> thres +alpha
                    #print(thres)
                    #print(up)

                    tips = [mp_hands.HandLandmark.THUMB_TIP, mp_hands.HandLandmark.INDEX_FINGER_TIP,\
                             mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_TIP,\
                             mp_hands.HandLandmark.PINKY_TIP]
                    # 人差し指が他の指よりも上にあるかどうかを確認
                    if index_finger_tip < min(thumb_tip, middle_finger_tip, ring_finger_tip, pinky_tip) and up:
                        print("Index finger is up")
                        self.index_finger_up_frames += 1  # 人差し指が上にあるフレーム数を増やす
                        if self.index_finger_up_frames >= 30:  # 人差し指が10フレーム以上上にある場合
                        # ここにドローンを上昇させる命令を追加
                            cv2.putText(image, 'Index finger is up', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                            self.index_finger_up_frames = 0  # フレーム数をリセットする
                            # 状態のチェック
                            if self.current_state == (TelloState.LAND or TelloState.FIN):
                                print(self.current_state)
                                print("takeoff")                          
                                self.tello.takeoff()  # ドローンを飛行させる
                                self.current_state = TelloState.TAKEOFF
                            else:
                                print("up")                          
                                self.tello.move_up(50)  # ドローンを飛行させる
                                if self.current_state != (TelloState.LAND or TelloState.FIN):
                                    self.current_state = TelloState.UP
                        
                    # 人差し指が他の指よりも下にあるかどうかを確認
                    elif index_finger_tip > max(thumb_tip, middle_finger_tip, ring_finger_tip, pinky_tip):
                        print("down")
                        self.index_finger_down_frames += 1  # 人差し指が上にあるフレーム数を増やす
                        if self.index_finger_down_frames >= 10:  # 人差し指が10フレーム以上下にある場合
                        # ここにドローンを上昇させる命令を追加
                            cv2.putText(image, 'Index finger is down', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                            self.index_finger_down_frames = 0  # フレーム数をリセットする
                            # 状態のチェック
                            if self.current_state != (TelloState.LAND or TelloState.FIN):
                                print("land")
                                self.tello.land()  # ドローンを着陸させる
                                self.current_state = TelloState.FIN
                                self.tello.end()#終了
                    elif self.analyze_peace_reverse(hand_landmarks):
                        print("ギャルピ")
                        self.gal_finger_frames +=1
                        if self.gal_finger_frames >=10:
                            self.gal_finger_frames =0
                            if self.current_state != (TelloState.LAND or TelloState.FIN) :
                                self.current_state = TelloState.GAL                   
                    elif self.are_all_fingers_open(hand_landmarks):
                        self.index_finger_open_frames += 1
                        print("OPEN")
                        if self.index_finger_open_frames >=20:
                            cv2.putText(image, 'hand opened', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                            self.index_finger_open_frames = 0
                            if self.current_state != (TelloState.LAND or TelloState.FIN) :
                                self.current_state = TelloState.OPEN
                    elif self.analyze_hand_landmarks(hand_landmarks):
                        if self.index_finger_left_frames >=10:
                            if self.current_state == TelloState.OPEN:
                                cv2.putText(image, 'Left flip', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                                print("left flip")
                                #FLIP LEFT
                                self.tello.flip_left()
                            elif self.current_state != (TelloState.LAND or TelloState.FIN) :
                                cv2.putText(image, 'Move left', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                                print("left move")
                                self.tello.move_left(50)
                                #self.tello.move("l", 50)
                                #move left
                            
                            self.index_finger_left_frames = 0
                            if self.current_state != (TelloState.LAND or TelloState.FIN):
                                self.current_state = TelloState.LEFT

                        elif self.index_finger_right_frames >=10:
                            if self.current_state == TelloState.OPEN:
                                print("right flip")
                                cv2.putText(image, 'Right flip', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                                self.tello.flip_right()
                                #FLIP RIGHT
                            elif self.current_state != (TelloState.LAND or TelloState.FIN):
                                cv2.putText(image, 'Move right', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                                print("right move")
                                self.tello.move_right(50)
                                #move right
                                #self.tello.move("r", 50)
                            
                            self.index_finger_right_frames = 0
                            if self.current_state != (TelloState.LAND or TelloState.FIN):
                                self.current_state = TelloState.RIGHT

                    # elif self.analyze_hand_landmarks_down(hand_landmarks):
                    #     if self.index_finger_left_frames >=10:
                    #         if self.current_state == TelloState.OPEN:
                    #             cv2.putText(image, 'Left curve', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                    #             #left curve
                    #             #self.tello.flip_left()
                    #         elif self.current_state == TelloState.TAKEOFF:
                    #             cv2.putText(image, 'Down left', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                    #             #self.tello.move("left", 50)
                    #             #move left
                            
                    #         self.index_finger_left_frames = 0
                    #         if self.current_state != TelloState.LAND:
                    #             self.current_state = TelloState.LEFT

                    #     elif self.index_finger_right_frames >=10:
                    #         if self.current_state == TelloState.OPEN:
                    #             cv2.putText(image, 'Right flip', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                    #             #self.tello.flip_right()
                    #             #curve RIGHT
                    #         elif self.current_state == TelloState.TAKEOFF:
                    #             cv2.putText(image, 'Move right', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                    #             #move right
                    #             #self.tello.move("right", 50)
                            
                    #         self.index_finger_right_frames = 0
                    #         if self.current_state != TelloState.LAND:
                    #             self.current_state = TelloState.RIGHT

                    else:
                        self.index_finger_up_frames = 0  # フレーム数をリセットする
                        self.index_finger_down_frames = 0  # フレーム数をリセットする
                        self.index_finger_open_frames = 0
                        self.index_finger_left_frames = 0
                        self.index_finger_right_frames = 0
                        self.gal_finger_frames =0
            cv2.putText(image, self.current_state.value, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow('MediaPipe Hands', image)

def main():
    tello = Tello_TEST()
    tello.start()

if __name__=="__main__":
    main()
   
