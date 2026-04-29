package project;

public class push {
    public StackState push_stack(StackState input, int newValue) {
        StackState result = new StackState();
        result.ptr = input.ptr + 1;
        for (int i = 1; i <= 16; i++) result.set(i, input.get(i));
        result.set(result.ptr, newValue);
        return result;
    }
}