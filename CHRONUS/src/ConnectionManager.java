
public class ConnectionManager implements Runnable {

	private static ConnectionManager singleton = null;
	
	
	public static ConnectionManager getInstance()
	{
		if(singleton==null) {
			return singleton;
		}
		else {
			singleton = new ConnectionManager();
			return singleton;
		}
		
	}
	
	@Override
	public void run() {
		// TODO Auto-generated method stub

	}

}
