/******************************************************************************************************************
* File:OrdersUI.java
* Course: Project Course
* Project: Fullfillment Center
* Copyright: Copyright (c) 2018 Carnegie Mellon University
* Versions:
*   1.0 April 2018 - Initial write of course order server demo (Lattanze).
*   2.0 November 2019 - Adapted for IITP project course. Changed database and order submission URL.
*
* Description: This class is the console for the an orders database. This interface uses a webservices client class
* to update the orderinfo MySQL database. 
*
* Parameters: None
*
* Internal Methods: 
*  String GetOrderCount ( String product ) - Returns the order count to the number of products ordered ensuring that 
*                                            the user input is correct and in bounds.
*  static void ParseAndPrint ( String ReturnQuery )-  Parses the return query and prints the records if there are 
*													  any.
*
* External Dependencies (one of the following):
*	- WSClientAPI - this class provides a restful interface to a node.js webserver (see Server.js and REST.js).
*
******************************************************************************************************************/

import java.util.Scanner;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.io.Console;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.*;
public class random_OrdersUI
{
	public static void main(String args[])
	{
		boolean done = false;						// main loop flag
		boolean error = false;						// error flag
		char    option;								// Menu choice from user
		Console c = System.console();				// Console string input
		Scanner keyboard = new Scanner(System.in);	// Console integer input

		String  customer = null;					// order date
		String 	response = null;					// response string from REST 
		String  orderid = null;						// Order ID
		String  red = null;							// red square count
		String  blue = null;						// blue square count
		String  green = null;						// green square count
		String  custaddress = null;					// customer address
	
		DateTimeFormatter dtf = null;				// Date object formatter
		LocalDate localDate = null;					// Date object
		WSClientAPI api = new WSClientAPI();		// RESTful api object
        int max_item=15;
        float max_time=20;
        float min_time=1;

        List<Integer> list = new ArrayList<>();
        list.add(101);
        list.add(102);
        list.add(103);
        list.add(201);
        list.add(202);
        list.add(203);

		/////////////////////////////////////////////////////////////////////////////////
		// Main UI loop
		/////////////////////////////////////////////////////////////////////////////////
		while (!done)
		{
            // Here we create a new order entry in the database

            Random r = new Random();
            char cu = (char)(r.nextInt(26) + 'a');
            customer=String.valueOf(cu);

            Random rand = new Random();
            int randomIndex = rand.nextInt(list.size());
            int custadd=list.get(randomIndex);
            custaddress=String.valueOf(custadd);

            System.out.println("====================================\n");

            Random random = new Random();
            int red_int = random.nextInt(max_item);
            int blue_int = random.nextInt(max_item);
            int green_int = random.nextInt(max_item);
            red 	= String.valueOf(red_int);
            blue 	= String.valueOf(blue_int);
            green	= String.valueOf(green_int);
            float sleep_time = (min_time + random.nextFloat() * (max_time - min_time))*1000;
            long sleep_time_i 	= (long)sleep_time;
            //String sleep_time_s 	= String.valueOf(sleep_time);

            System.out.println("Creating the following order:");
            System.out.println("==============================");
            System.out.println(" Customer name:" 	+ customer);
            System.out.println(" Customer name:" 	+ custaddress);
            System.out.println(" red square(s):" 	+ red);
            System.out.println(" blue square(s):" 	+ blue);
            System.out.println(" green square(s):" 	+ green);
            System.out.println(" Sleep time(sec):" 	+ sleep_time/1000);
            System.out.println("==============================");

            try
            {
                System.out.println("\nCreating order...");
                response = api.newOrder(customer, red, blue, green, custaddress);

            } catch(Exception e) {

                System.out.println("Request failed:: " + e);
            }

            if (!ErrorQueryStatus(response))
            {
                System.out.print("Order created successfully! ");
            } else {
                System.out.print("Error adding order. ");
            }

            //System.out.println("Press enter to continue..." );
            //c.readLine();
            //Thread.sleep(100000);

            try
            {
                TimeUnit.MILLISECONDS.sleep(sleep_time_i);
            }
            catch(InterruptedException ex)
            {
                Thread.currentThread().interrupt();
            }
            option = ' '; //Clearing option. This in case the user enterd X/x the program will not exit.
		} // while

  	} // main


  	//////////////////////////////////////////////////////////////////////////////////
	// This method returns the number of products ordered ensuring that the user input
	// is correct an in bounds.
	//////////////////////////////////////////////////////////////////////////////////

  	private static String GetOrderCount ( String product )
  	{			
		boolean done=false;						    // loop flag
		boolean error=true;							// error flag
		Scanner in = new Scanner(System.in);		// Console integer input
		Integer ordercount=0;						// Number of items

		while( !done )
		{
       		System.out.print("How many " + product + " products >> ");

        	if (in.hasNextInt()) 
        	{
        		ordercount = in.nextInt();
       			error = false;
       			done = true;

       		} else {

        		System.out.println("Must enter positive integers...");
            	in.next();
            	System.out.println();
            	error = true;

            } // if
        } // while

		if (!error)
			if (ordercount < 0 )
			{
				System.out.println( "Product quantities must be positive...");
			} else  {
				System.out.println("OK you specified " + ordercount + " " + product + " products.");
				done = true;
			} // if

		return(ordercount.toString());

	} // GetOrderCount

	//////////////////////////////////////////////////////////////////////////////////
	// Returns the error code from the return query string.
	//////////////////////////////////////////////////////////////////////////////////

	private static boolean ErrorQueryStatus ( String ReturnQuery )
	{
		int lefttoken = ReturnQuery.indexOf(":");
		int righttoken = ReturnQuery.indexOf(",");		

		String status = ReturnQuery.substring(lefttoken + 1, righttoken);

		return( status.equalsIgnoreCase("true") );

	}

	//////////////////////////////////////////////////////////////////////////////////
	// Parses the return query and prints the records if there are any.
	//////////////////////////////////////////////////////////////////////////////////

	private static void ParseAndPrint ( String ReturnQuery )
	{
		int 	begintoken = ReturnQuery.indexOf("[");
		int 	endtoken = ReturnQuery.indexOf("]");		
		int 	lefttoken;
		int 	righttoken;
		int 	beginfield;
		int     endfield;
		int 	cnt;
		String 	record;
		boolean	done, endrecord;

		if (begintoken+1 == endtoken)
		{
			System.out.println("\nThere are no matching records...");

		} else {

			// in this loop we parse out each record

			done = false;
			cnt=1;
			while (!done)
			{	
				// find next record, note records are bound by {}
				lefttoken = ReturnQuery.indexOf("{", begintoken);
				righttoken = ReturnQuery.indexOf("}", begintoken);

				// here we get rid of all the " marks
				record = ReturnQuery.substring(lefttoken+1, righttoken);
				record = record.replace("\"", "");

				// here we start parsing the individual record and print it.
				endrecord = false;
				beginfield = 0;
				endfield = record.indexOf(",", beginfield);
				System.out.println("Record " + record.substring(beginfield, endfield));
				System.out.println("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~");

				while(!endrecord)
				{
					beginfield = endfield + 1;
					endfield = record.indexOf(",", beginfield);

					if (endfield != -1)
					{
						System.out.println(">> "+record.substring(beginfield, endfield));
					} else {
						System.out.println(">> "+record.substring(beginfield, record.length()-1));							
						endrecord = true;
					}
				}

				// here we check to see if we are don processing records				
			
				if (ReturnQuery.indexOf("]", begintoken) == righttoken+1)
				{
					done = true;
				} else {
					begintoken = righttoken + 1;
					cnt++;
					System.out.println();
				}
			}

			System.out.println("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~");
			System.out.println("Done:: " + cnt + " records found.");
		}
	}

} // OrdersUI
