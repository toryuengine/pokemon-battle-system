#include <iostream>
#include <cstdlib> // std::system のために必要
#include <string>
#include <vector>

//ステータス実数値
struct Status {
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
struct individualValue {
    int hp;
    int attack;
    int defense;
    int sp_attack;
    int sp_defence;
    int speed;
};

//努力値
struct effortValue {
    int hp;
    int attack;
    int defense;
    int sp_attack;
    int sp_defence;
    int speed;
};


struct savedata {
    int id;
    int identifier;
    int lv; //レベル
    individualValue indivisual;//個体値構造体
    effortValue effort;//努力値構造体
    int personality;//性格
};

class CharaCter {
    private:
        savedata data;
        Status status;
        Racial racial;//種族値構造体

    //ステータス実数値を計算して、status構造体に値を入れる
        void setStatus() {
            //種族値の取得
            getRacial();

            status.hp = calcStatusHP(data.lv, racial.hp, data.indivisual.hp, data.effort.hp);
            status.attack = calcStatus(data.lv, racial.attack, data.indivisual.attack, data.effort.attack);
            status.defense = calcStatus(data.lv, racial.defense, data.indivisual.defense, data.effort.defense);
            status.sp_attack = calcStatus(data.lv, racial.sp_attack, data.indivisual.sp_attack, data.effort.sp_attack);
            status.sp_defence = calcStatus(data.lv, racial.sp_defence, data.indivisual.sp_defence, data.effort.sp_defence);
            status.speed = calcStatus(data.lv, racial.speed, data.indivisual.speed, data.effort.speed);

            //性格を適用する
            applyPersonality();
        };

        

        //種族値をsavedataのidから検索して、構造体に保存する
        void getRacial() {
            //検索は後で追加
            //例）バクフーン
            racial = {78, 84, 78, 109, 85, 100};

        }

        //ステータスを算出する
        //レベル, 種族値, 個体値, 努力値
        int calcStatus(int lv, int rac, int ind, int eff) {
            int calkEffort = eff / 4;
            int calk1 = rac * 2 + ind + calkEffort;
            int calk2 = calk1 * lv;
            int calk3 = calk2 / 100;
            int finalStatus = calk3 + 5;

            return finalStatus;
        };

        //HPを算出する
        //レベル, 種族値, 個体値, 努力値
        int calcStatusHP(int lv, int rac, int ind, int eff) {
            int calkEffort = eff / 4;
            int calk1 = rac * 2 + ind + calkEffort;
            int calk2 = calk1 * lv;
            int calk3 = calk2 / 100;
            int finalStatus = calk3 + lv + 10;

            return finalStatus;
        };

        //性格補正の適用
        void applyPersonality() {
            switch (data.personality){
            case 1://いじっぱり
                status.attack = status.attack * 110 / 100;
                status.sp_attack = status.sp_attack * 90 / 100;
                break;

            case 2://おくびょう
                status.speed = status.speed * 110 / 100;
                status.attack = status.attack * 90 / 100;
                break;

            case 3://がんばりや
                break;

            case 4://さみしがり
                status.attack = status.attack * 110 / 100;
                status.defense = status.defense * 90 / 100;
                break;

            case 5://ゆうかん
                status.attack = status.attack * 110 / 100;
                status.speed = status.speed * 90 / 100;
                break;

            case 6://やんちゃ
                status.attack = status.attack * 110 / 100;
                status.sp_defence = status.sp_defence * 90 / 100;
                break;

            case 7://ずぶとい
                status.defense = status.defense * 110 / 100;
                status.attack = status.attack * 90 / 100;
                break;

            case 8://すなお
                break;

            case 9://のんき
                status.defense = status.defense * 110 / 100;
                status.speed = status.speed * 90 / 100;
                break;

            case 10://わんぱく
                status.defense = status.defense * 110 / 100;
                status.sp_attack = status.sp_attack * 90 / 100;
                break;

            case 11://のうてんき
                status.defense = status.defense * 110 / 100;
                status.sp_defence = status.sp_defence * 90 / 100;
                break;

            case 12://せっかち
                status.speed = status.speed * 110 / 100;
                status.defense = status.defense * 90 / 100;
                break;

            case 13://まじめ
                break;

            case 14://ようき
                status.speed = status.speed * 110 / 100;
                status.sp_attack = status.sp_attack * 90 / 100;
                break;

            case 15://むじゃき
                status.speed = status.speed * 110 / 100;
                status.sp_defence = status.sp_defence * 90 / 100;
                break;

            case 16://ひかえめ
                status.sp_attack = status.sp_attack * 110 / 100;
                status.attack = status.attack * 90 / 100;
                break;

            case 17://おっとり
                status.sp_attack = status.sp_attack * 110 / 100;
                status.defense = status.defense * 90 / 100;
                break;

            case 18://うっかりや
                status.sp_attack = status.sp_attack * 110 / 100;
                status.sp_defence = status.sp_defence * 90 / 100;
                break;

            case 19://れいせい
                status.sp_attack = status.sp_attack * 110 / 100;
                status.speed = status.speed * 90 / 100;
                break;

            case 20://てれや
                break;

            case 21://おだやか
                status.sp_defence = status.sp_defence * 110 / 100;
                status.attack = status.attack * 90 / 100;
                break;

            case 22://おとなしい
                status.sp_defence = status.sp_defence * 110 / 100;
                status.defense = status.defense * 90 / 100;
                break;

            case 23://なまいき
                status.sp_defence = status.sp_defence * 110 / 100;
                status.speed = status.speed * 90 / 100;
                break;

            case 24://しんちょう
                status.sp_defence = status.sp_defence * 110 / 100;
                status.sp_attack = status.sp_attack * 90 / 100;
                break;

            case 25://きまぐれ
                break;

            default:
                break;
            };

        };

    public:
        //setと同時にステータス実数地を計算する
        void setData(savedata arg) {
            data = arg;
            setStatus();
        };


        //ステータスを取り出す
        Status getStatus() const {
            return status;
        };
};

class Basic_status_calc {
    private:
        Racial Typhlosion = {50, 78, 84, 78, 109, 85, 100};
        Racial Swampert = {50, 100, 110, 90, 85, 90, 60};
        savedata data;
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
            status.hp = calcStatus(arg.lv, arg.hp);
            status.attack = calcStatus(arg.lv, arg.attack);
            status.defense = calcStatus(arg.lv, arg.defense);
            status.sp_attack = calcStatus(arg.lv, arg.sp_attack);
            status.sp_defence = calcStatus(arg.lv, arg.sp_defence);
            status.speed = calcStatus(arg.lv, arg.speed);
        };

        //ステータスを算出する
        int calcStatus(int lv, int status) {
            int calkEffort = 252 / 4;
            int calk1 = status * 2 + 31 + calkEffort;
            int calk2 = calk1 * lv;
            int calk3 = calk2 / 100;
            int finalStatus = calk3 + 5;

            return finalStatus;
        };

        savedata getStatus() {
            return data;
        };

        void setCharacter() {
            data.id = 00001;
            data.identifier = 00001;
            data.lv = 50;
            data.indivisual = {31, 31, 31, 31, 31, 31};
            data.effort = {4, 0, 0, 252, 0, 252};
            data.personality = 16;//控えめ
        };
};


int main() {
    system("chcp 65001");
    Basic_status_calc basic;
    basic.setCharacter();
    savedata data = basic.getStatus();

    CharaCter character;
    character.setData(data);
    Status status = character.getStatus();
    
    //確認のための出力
    std::cout << status.hp << std::endl;
    std::cout << status.attack << std::endl;
    std::cout << status.defense << std::endl;
    std::cout << status.sp_attack << std::endl;
    std::cout << status.sp_defence << std::endl;
    std::cout << status.speed << std::endl;

    return 0;
    // while (true){
    //     std::cout << "バクフーン" ;
    //     std::cout << "" ;
    //     std::cout << "ラグラージ" ;
    //     std::cout << "" ;
    //     std::cout << "フシギバナ" ;
        
    // }

    // Basic_status_calc basic;
    // Racial me = basic.getPokemon1();
    // basic.setRacial(me);
    // Status status = basic.getStatus();
    
    // std::cout << status.hp << std::endl;
    // std::cout << status.attack << std::endl;
    // std::cout << status.defense << std::endl;
    // std::cout << status.sp_attack << std::endl;
    // std::cout << status.sp_defence << std::endl;
    // std::cout << status.speed << std::endl;
    // return 0;


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
