#include <iostream>
#include <cstdlib> // std::system のために必要
#include <string>
#include <vector>
struct Status {
    int lv;
    int hp;
    int attack;
    int defense;
    int sp_attack;
    int sp_defence;
    int speed;
};

//種族値
struct Racial {
    int lv;
    int hp;
    int attack;
    int defense;
    int sp_attack;
    int sp_defence;
    int speed;
};

//個体値
struct individual {
    int lv;
    int hp;
    int attack;
    int defense;
    int sp_attack;
    int sp_defence;
    int speed;
};

class Basic_status_calc {
    private:
        Racial Typhlosion = {50, 84, 78, 109, 85, 100};
        Racial Swampert = {50, 100, 110, 90, 85, 90, 60};
        
        Status status;

    public:
        int name;
        Racial getPokemon1() const {
            return Typhlosion;
        }

        //種族値をセットする
        void setRacial(const Racial arg) {
            Racial racial = arg;
            setStatus(racial);
        };

        void setStatus(Racial arg) {
            status.attack = calkAtk(arg);
            status.hp = calkHp(arg);
        };



        //HPの算出
        int calkHp(Racial arg) {
            int calkEffort = 252 / 4; 
            int calk1 = arg.hp * 2 + 31 + calkEffort;
            int calk2 = calk1 * arg.lv;
            int calk3 = calk2 / 100;

            int finalHp = calk3 + 5;
            
            return finalHp;

        };

        //こうげき力の算出
        int calkAtk(Racial arg){
            int calkEffort = 252 / 4; 

            // 1. カッコ内の合計を計算 (種族値×2 + 個体値 + 努力値/4)
            int calk1 = arg.attack * 2 + 31 + calkEffort;

            // 2. 先に「レベル」を掛ける（★ここが修正ポイント）
            int calk2 = calk1 * arg.lv;

            // 3. その後、100で割って切り捨てる（★ここが修正ポイント）
            int calk3 = calk2 / 100;

            // 4. 最後に 5 を足す
            int finalAtk = calk3 + 5;

            return finalAtk;
        };


        Status getStatus() {
            return status;
        };
};


int main() {
    Basic_status_calc basic;
    Racial me = basic.getPokemon1();
    basic.setRacial(me);
    Status status = basic.getStatus();
    std::cout << status.attack << std::endl;
    std::cout << status.hp << std::endl;
    return 0;


    // int i = 1;
    // Status Typhlosion = {220, 15}; //ラグラージ
    // Status Swampert = {204, 22};//バクフーン
    // std::system("chcp 65001"); // コンソールをUTF-8モードに変更
    // bool battle = true;

    // while (battle) {
    //     std::cout << "ターン" << i << std::endl;

    //     // if-else文を使うことで、条件分岐を1回にまとめる
    //     // if (i % 2 != 0) {
            
    //     Swampert.hp = Swampert.hp - Typhlosion.attack;
    //     std::cout << "ラグラージの残りＨＰ" << Swampert.hp << std::endl;

    //     // } else {
    //     Typhlosion.hp = Typhlosion.hp - Swampert.attack;
    //     std::cout << "バクフーンの残りＨＰ" << Typhlosion.hp << std::endl;
    //     // }

    //     std::cin.get(); 
    //     i++;

    // //戦闘終了
    //     if(Typhlosion.hp <= 0) {
    //         battle = false;
    //     }else if (Swampert.hp <= 0) {
    //         battle = false;
    //     }
    // }
    // std::cout << "戦闘終了" << std::endl;
    // return 0; // 無限ループのため実際には到達しません
};
