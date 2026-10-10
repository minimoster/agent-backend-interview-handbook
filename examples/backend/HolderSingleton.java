public final class HolderSingleton {
    private final String mode;
    private HolderSingleton() { this.mode = "ready"; }
    private static final class Holder {
        private static final HolderSingleton INSTANCE = new HolderSingleton();
    }
    public static HolderSingleton getInstance() { return Holder.INSTANCE; }
    public String mode() { return mode; }
}
