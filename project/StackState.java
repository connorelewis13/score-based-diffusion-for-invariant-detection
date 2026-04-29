package project;

public class StackState {
    public int ptr;
    public int v1, v2, v3, v4, v5, v6, v7, v8, v9, v10;
    public int v11, v12, v13, v14, v15, v16;

    public static StackState fromArray(int[] arr) {
        StackState s = new StackState();
        s.ptr = arr[0];
        s.v1 = arr[1];   s.v2 = arr[2];   s.v3 = arr[3];   s.v4 = arr[4];
        s.v5 = arr[5];   s.v6 = arr[6];   s.v7 = arr[7];   s.v8 = arr[8];
        s.v9 = arr[9];   s.v10 = arr[10]; s.v11 = arr[11]; s.v12 = arr[12];
        s.v13 = arr[13]; s.v14 = arr[14]; s.v15 = arr[15]; s.v16 = arr[16];
        return s;
    }

    public int[] toArray() {
        return new int[]{ptr, v1, v2, v3, v4, v5, v6, v7, v8, v9,
                         v10, v11, v12, v13, v14, v15, v16};
    }

    public int get(int i) {
        switch (i) {
            case 1: return v1;   case 2: return v2;   case 3: return v3;
            case 4: return v4;   case 5: return v5;   case 6: return v6;
            case 7: return v7;   case 8: return v8;   case 9: return v9;
            case 10: return v10; case 11: return v11; case 12: return v12;
            case 13: return v13; case 14: return v14; case 15: return v15;
            case 16: return v16;
            default: throw new IllegalArgumentException("Invalid index: " + i);
        }
    }

    public void set(int i, int val) {
        switch (i) {
            case 1: v1 = val; break;  case 2: v2 = val; break;  case 3: v3 = val; break;
            case 4: v4 = val; break;  case 5: v5 = val; break;  case 6: v6 = val; break;
            case 7: v7 = val; break;  case 8: v8 = val; break;  case 9: v9 = val; break;
            case 10: v10 = val; break; case 11: v11 = val; break; case 12: v12 = val; break;
            case 13: v13 = val; break; case 14: v14 = val; break; case 15: v15 = val; break;
            case 16: v16 = val; break;
            default: throw new IllegalArgumentException("Invalid index: " + i);
        }
    }
}