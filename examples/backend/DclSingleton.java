public final class DclSingleton {
    private static volatile DclSingleton instance;
    private final String mode;
    private DclSingleton() { this.mode = "ready"; }
    public static DclSingleton getInstance() {
        DclSingleton result = instance;
        if (result == null) {
            synchronized (DclSingleton.class) {
                result = instance;
                if (result == null) {
                    result = new DclSingleton();
                    instance = result;
                }
            }
        }
        return result;
    }
    public String mode() { return mode; }
}
