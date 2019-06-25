package de.ostfalia.zell.praktomat;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.text.NumberFormat;
import java.util.List;

import java.io.StringWriter;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerConfigurationException;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import org.w3c.dom.Document;
import org.w3c.dom.Element;

import org.junit.internal.JUnitSystem;
import org.junit.runner.Description;
import org.junit.runner.JUnitCore;
import org.junit.runner.Result;
import org.junit.runner.notification.Failure;
import org.junit.runner.notification.RunListener;


public class JunitProFormAListener extends RunListener {

    private final PrintStream writer;
    private Document doc = null;
    private Element subtestsResponse;
    private int counterFailed = 0;
    
//    ByteArrayOutputStream baos = new ByteArrayOutputStream();
    
    
    // parameters of current test
    private boolean passed = true;
    private int counter = 0;
    Element score;
    Element feedbackList;
    Element feedbackTitle;    
    

    public JunitProFormAListener() {
    	writer = System.out;
        //System.setOut(new PrintStream(baos));    	
    }

    public JunitProFormAListener(PrintStream writer) {
        this.writer = writer;
    }

    @Override    
    public void testRunStarted(Description description) throws ParserConfigurationException {
        DocumentBuilderFactory docFactory = DocumentBuilderFactory.newInstance();
        DocumentBuilder docBuilder = docFactory.newDocumentBuilder();
        doc = docBuilder.newDocument();  
        
        //Element testResponse = doc.createElement("test-response");
        //doc.appendChild(testResponse);      
        subtestsResponse = doc.createElement("subtests-response");
        doc.appendChild(subtestsResponse);          
        //testResponse.appendChild(subtestsResponse);          
    }
    
    @Override
    public void testRunFinished(Result result) {
    	
        // Transform Document to XML String
        TransformerFactory tf = TransformerFactory.newInstance();
        Transformer transformer;
		try {
			transformer = tf.newTransformer();
	        transformer.setOutputProperty(OutputKeys.OMIT_XML_DECLARATION, "yes");
	        transformer.setOutputProperty(OutputKeys.INDENT, "yes");	        
	        StringWriter xmlWriter = new StringWriter();
	        DOMSource root = new DOMSource(doc);
	        transformer.transform(root, new StreamResult(writer));
	        
	        // print the String value of final xml document        
	        getWriter().println(xmlWriter.getBuffer().toString());    				
		} catch (TransformerException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
	        getWriter().print(e.getMessageAndLocation());    				
		}

        
//        printHeader(result.getRunTime());
    }

    // -------------------------------
    
    @Override
    public void testStarted(Description description) {
    	String title = "";
    	String desc = new String(description.toString());
    	desc = desc.substring(0, desc.indexOf("("));
        for (String w : desc.split("(?<!(^|[A-Z]))(?=[A-Z])|(?<!^)(?=[A-Z][a-z])")) {
        	if (title.isEmpty() && w.equalsIgnoreCase("test"))
        		continue;
        	
        	title += w + ' ';
        }    

        title = title.trim();
        passed = true;   
        counter ++;
        
    	// create xml 
    	
    	
        /*<subtest-response id = 's1'>
          <test-result>        
        
            <result><score>1.0</score></result>
          
            <feedback-list>
              <student-feedback level="info">
                <title>Even Number Of Characters</title>
              </student-feedback>
            </feedback-list>

        </test-result>
        </subtest-response>*/
    
        Element subtestResponse = doc.createElement("subtest-response");
        subtestResponse.setAttribute("id", "junit" +  counter);
        subtestsResponse.appendChild(subtestResponse);
        
        // Create First Name Element
        Element testResult = doc.createElement("test-result");
        subtestResponse.appendChild(testResult);
        
        Element result = doc.createElement("result");
        testResult.appendChild(result);
        score = doc.createElement("score");
        result.appendChild(score);
    	
        feedbackList = doc.createElement("feedback-list");
        testResult.appendChild(feedbackList);
        
        
        feedbackTitle = doc.createElement("student-feedback");        
        feedbackList.appendChild(feedbackTitle);
        Element xmlTitle = doc.createElement("title");
        feedbackTitle.appendChild(xmlTitle);    
        xmlTitle.appendChild(doc.createTextNode(title));        
    }

    @Override
    public void testFinished(Description description) {
        // todo: bei failed noch den Fehlertext

    	if (passed) {
            score.appendChild(doc.createTextNode("1.0"));    		
            feedbackTitle.setAttribute("level", "info");
        }
    	else {
            score.appendChild(doc.createTextNode("0.0"));            		
            feedbackTitle.setAttribute("level", "error");
    	}
    }
    
    
    @Override
    public void testFailure(Failure failure) {
        Element xmlFailure = doc.createElement("content");
        xmlFailure.setAttribute("format", "plaintext");        
        feedbackTitle.appendChild(xmlFailure);
        
        if (failure.getMessage() != null)
        	xmlFailure.appendChild(doc.createTextNode(failure.getMessage()));
        else
        	xmlFailure.appendChild(doc.createTextNode("N/A"));
        
        Element teacherFeedback = doc.createElement("teacher-feedback");        
        feedbackList.appendChild(teacherFeedback);
        Element xmlTitle = doc.createElement("title");
        teacherFeedback.appendChild(xmlTitle);    
        xmlTitle.appendChild(doc.createTextNode("Exception"));        

        Element xmlException = doc.createElement("content");
        xmlException.setAttribute("format", "plaintext");        
        teacherFeedback.appendChild(xmlException);     
        String teacherText = failure.toString() + "\n" + 
        		failure.getTrace(); 
        		
        xmlException.appendChild(doc.createTextNode(teacherText));  
        
        
        // writer.append("\n");
        //printFailure(failure, "    Failure: ");    	
        // getWriter().println();
        
        passed = false;  
        counterFailed++;      
    }

    // -------------------------------
    
    
    
    
    @Override
    public void testIgnored(Description description) {
        //writer.append('I');
    }

    /*
      * Internal methods
      */

    private PrintStream getWriter() {
        return writer;
    }


    protected void printFailures(Result result) {
        List<Failure> failures = result.getFailures();
        if (failures.isEmpty()) {
            return;
        }
               
        
        int i = 1;
        for (Failure each : failures) {
            printFailure(each, "" + i++);
        }
    }

    protected void printFailure(Failure each, String prefix) {
        getWriter().println(prefix + " " + each.getMessage());
        //getWriter().print(each.getTrimmedTrace());
    }

    protected void printFooter(Result result) {
        getWriter().println();
        
        float score = ((float)(counter - counterFailed))/counter;
        getWriter().print("Score: " + score);
    	
/*        
        if (result.wasSuccessful()) {
            getWriter().println();
            getWriter().print("OK");
            getWriter().println(" (" + result.getRunCount() + " test" + (result.getRunCount() == 1 ? "" : "s") + ")");

        } else {
            getWriter().println();
            getWriter().println("FAILURES!!!");
            getWriter().println("Tests run: " + result.getRunCount() + ",  Failures: " + result.getFailureCount());
        }
        getWriter().println();
*/        
    }
    
/*    protected testRunFinished(Result result) {
    	
    }
*/
    /**
     * Returns the formatted string of the elapsed time. Duplicated from
     * BaseTestRunner. Fix it.
     */
    protected String elapsedTimeAsString(long runTime) {
        return NumberFormat.getInstance().format((double) runTime / 1000);
    }
    
    public static void main(String[] args) {
        if (args.length == 0) {
        	System.err.println("Invalid argument number. Usage: program testclass (without extension)");
	        System.exit(1);			 			
        }
		JUnitCore core= new JUnitCore();
		JunitProFormAListener listener = new JunitProFormAListener();
		core.addListener(listener);

		try {
			core.run(Class.forName(args[0]));
		} catch (ClassNotFoundException e) {
			// TODO Auto-generated catch block
			System.err.println(e.getMessage());
	    	System.err.println("Class " + args[0] + " not found. Usage: program testclass (without extension)");
	        System.exit(1);			 			
		}
	}    
}
