
public class MessageHandler implements Runnable {

	private static MessageHandler singleton = null;
	
	
	public static MessageHandler getInstance()
	{
		if(singleton!=null) {
			return singleton;
		}
		else {
			singleton = new MessageHandler();
			return singleton;
		}
		
	}	
	
	@Override
	public void run() {
		// TODO Auto-generated method stub

	}

	
	
	class FingerTable{
		int degree = Globals.hashDegree;
		Node[] table;
	}
}
