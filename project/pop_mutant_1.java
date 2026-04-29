package project;

public class pop_mutant_1 {
    public StackState pop_stack(StackState input) {
        StackState result = new StackState();
        result.ptr = input.ptr; //removed stack increment
        for (int i = 1; i <= 16; i++) result.set(i, input.get(i));
        result.set(input.ptr, 0);
        return result;
    }
}