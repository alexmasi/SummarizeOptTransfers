/*
 * *   Copyright (C) 2017 Mukul S. Bansal (mukul.bansal@uconn.edu).
 * *
 * *   This program is free software: you can redistribute it and/or modify
 * *   it under the terms of the GNU General Public License as published by
 * *   the Free Software Foundation, either version 3 of the License, or
 * *   (at your option) any later version.
 * *
 * *   This program is distributed in the hope that it will be useful,
 * *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 * *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * *   GNU General Public License for more details.
 * *
 * *   You should have received a copy of the GNU General Public License
 * *   along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * */




#define THRESHOLD 100

#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <vector>
#include <set>
#include <ctype.h>
#include <string.h>
//#include <stdlib>
//#include <boost/lexical_cast.hpp>



using namespace std;


struct data     // for parsing data from files into array
	{
		string genenode;
		bool isLeaf;
		int event; // 0 = speciation, 1 = duplication, 2 = transfer
		string mapping;
		string recipient;
	};


struct data2   // for storing event counts
{
	int spec;
	int dup;
	int tran;
	bool isLeaf;

};


struct data3   // for storing all the mappings from a gene node
{
	string node;
	int count;
	string recnode;	// and recipients
	int reccount;
};


int main (int argc, char* argv[])
{
	char filename[100];
	char s[100];
	string line, part1, part2, part3;
	string numsols;    // to store the line containing the total number of optimal solutions
// stringstream out;
// string s;

// int numfiles = boost::lexical_cast<int>(argv[2] );

	int numfiles = 1;
	int i;
	int FilesFullCount = 0;   // to check is all the input reconciliation files have run to completion (i.e., they didn't crash)
	bool FilesFullFlag = false;


	vector< vector<data> > array;
	vector<data> arrayline;

	vector<data2> counts;
	data2 tempcounts;


	vector< vector<data3> > mappings;
	vector<data3> tempmappings;
	data3 tempmap;

	vector<data3> frequentmapping;


// Added vectors to mirror the functionality of mapping vectors
	vector< vector<data3> > recipients;
	vector<data3> temprecipients;
	data3 temprec;

	vector<data3> frequentrecipient;


	size_t found;
	size_t found2;
	size_t found3;

	int start = 0;
	// outer loop to iterate over the different input files
  	for(i = 1; ; i++)
	{
//		filename.clear();
//		out << i;
//		s = out.str();
		arrayline.clear();

		sprintf(s,"%d",i);
//		itoa(i, s, 10);
		strcpy (filename,argv[1]);
		strcat(filename,s);
		//filename = argv[1] + s; // prepare the file name

		start = 0;    // to keep track of when we are in the reconcliation block

		ifstream myfile;
		myfile.open(filename);
		if (myfile.is_open ())
		{
			while (myfile.good ()) // inner lop to iterate over all lines in the file
			{

				data temp;
				getline (myfile, line);

				found3 = line.find("optimal");   // to copy the number of optimal solutions
				if (found3!=string::npos)
				{
					FilesFullCount++;
					numsols = line;
//					cout << numsols << endl;

				}


				found=line.find("Reconciliation:");
				if (found!=string::npos)
				{
					start = 1;
					continue;
				}

				if (start == 1)
				{
					found=line.find(":");
					if(found == string::npos)
						start = 0;
				}


				if (start == 1)
				{
//cout << line << endl;
					found=line.find(":");
					if(found ==string::npos)
						cout << "ERROR!!" << endl;

					part1 = line.substr (0, found);
					temp.genenode = part1;
					part2 = line.substr(found+1);

					found=part2.find("Leaf");
					if(found !=string::npos)
						temp.isLeaf = true;
					else temp.isLeaf = false;

					found=part2.find("Speciation");
					if(found !=string::npos)
					{
						temp.event = 0;
						found = part2.find("-->");
						part3 = part2.substr(found+4);
						temp.mapping = part3;
					}

					found=part2.find("Duplication");
					if(found !=string::npos)
					{
						temp.event = 1;
						found = part2.find("-->");
						part3 = part2.substr(found+4);
						temp.mapping = part3;
					}

					found=part2.find("Transfer");
					if(found !=string::npos)
					{
						temp.event = 2;
						found = part2.find("-->");
						found2 = part2.find(",", found+4);
						part3 = part2.substr(found+4, (found2 - (found + 4)));
						temp.mapping = part3;
						temp.recipient = part2.substr(found2 + 16);

					}

					arrayline.push_back(temp);
//					cout << temp.isLeaf << " " << temp.genenode << " " << temp.event << " " << temp.mapping  << " " << temp.recepient << endl;
				}


			}

			myfile.close ();

			// fill the main array with the parsed data from all files
			array.push_back(arrayline);
		}
		 else
		 {
			 if (i ==1)
			 {
				 cout << "ERROR: Unable to open reconciliation files. Please ensure the files' filename-prefix and path are correct." << endl;
				 return 1;
			 }

			 else
				 cout << "Processed " << i-1 << " files" << endl;

			 if (FilesFullCount == (i-1))
			 {
				 FilesFullFlag = true;
			 }

			 break;
		 }


	}


	int x = array[0].size();
	int y = array.size();


//	cout << y << endl;


	// process to consolidate events

	for (int i = 0; i < x; i++)
	{

		tempcounts.spec = 0;
		tempcounts.tran = 0;
		tempcounts.dup = 0;
		tempcounts.isLeaf = false;

		for(int j = 0; j < y ; j++)
		{

			if (array[j][i].isLeaf == true)
			{
				tempcounts.isLeaf = true;
				break;
			}

			if (array[j][i].event == 0)
			{
				tempcounts.spec = tempcounts.spec + 1;
			}
			else if (array[j][i].event == 1)
			{
				tempcounts.dup = tempcounts.dup + 1;
			}
			else if (array[j][i].event == 2)
			{
				tempcounts.tran = tempcounts.tran + 1;
			}
		}

		counts.push_back(tempcounts);
	}



	// process to consolidate the mappings for any given gene node.


	multiset<string> myset;
	multiset<string>::iterator it;


	for (int i = 0; i < x; i++)
	{
		tempmappings.clear();
		myset.clear();

		for(int j = 0; j < y ; j++)
		{

			if (array[j][i].isLeaf == true)
			{
				break;
			}

			myset.insert(array[j][i].mapping);
		}

		if (array[0][i].isLeaf == true)
		{
			tempmap.node = " ";
			tempmap.count = -1;

			tempmappings.push_back(tempmap);
		}

		else
		{

			for (it=myset.begin(); it!=myset.end(); it++)
			{

				tempmap.node.assign(*it);
				tempmap.count = 1;

				// remove the extra wierd characters from the end of *it char array.
				char c;
				for (int k = 0; k < tempmap.node.size(); k++)
				{
					char c = tempmap.node[k];

					if (iscntrl(c))
						tempmap.node.erase(k,1);
				}

				// cout << tempmap.node.size() << "    " << tempmap.node << "XYZ" << tempmap.node.size() <<endl;
				if (tempmappings.size() > 0)
				{

					if (tempmappings[tempmappings.size()-1].node == tempmap.node)
						{

							tempmappings[tempmappings.size()-1].count = tempmappings[tempmappings.size()-1].count + 1;
						}
					else
						tempmappings.push_back(tempmap);
				}
				else
					tempmappings.push_back(tempmap);
			}
		}

		mappings.push_back(tempmappings);
	}






	// process to consolidate the recipient mappings for any given gene node.


for (int i = 0; i < x; i++)
	{
		temprecipients.clear();
		myset.clear();

		for(int j = 0; j < y ; j++)
		{
			if (array[j][i].event == 2)
			{
				myset.insert(array[j][i].recipient);
			}
		}

		// if (array[0][i].isLeaf == true)
		// {
		// 	temprec.recnode = " ";
		// 	temprec.reccount = -1;
		//
		// 	temprecipients.push_back(tempmrec);
		// }

		// else
		// {

			for (it=myset.begin(); it!=myset.end(); it++)
			{

				temprec.recnode.assign(*it);
				temprec.reccount = 1;

				// remove the extra wierd characters from the end of *it char array.
				char c;
				for (int k = 0; k < temprec.recnode.size(); k++)
				{
					char c = temprec.recnode[k];

					if (iscntrl(c))
						temprec.recnode.erase(k,1);
				}

				// cout << tempmap.node.size() << "    " << tempmap.node << "XYZ" << tempmap.node.size() <<endl;
				if (temprecipients.size() > 0)
				{

					if (temprecipients[temprecipients.size()-1].recnode == temprec.recnode)
						{

							temprecipients[temprecipients.size()-1].reccount += 1;
						}
					else
						temprecipients.push_back(temprec);
				}
				else
					temprecipients.push_back(temprec);
			}
		// }

		recipients.push_back(temprecipients);
	}











	// process to choose the most frequent mapping for any given gene node


	for (int i = 0; i < x; i++)
	{
		tempmappings.clear();
		int best = 0;

		int mapsize = mappings[i].size();

		if (array[0][i].isLeaf == true)
		{
			tempmap.node = " ";
			tempmap.count = -1;
			frequentmapping.push_back(tempmap);
		}

		else
		{
			for(int j = 0; j< mapsize; j++)
			{
				if(mappings[i][j].count > best)
				{
					best = mappings[i][j].count;
					tempmap.node = mappings[i][j].node;
					tempmap.count = mappings[i][j].count;
				}
			}

			frequentmapping.push_back(tempmap);

		}

	}



	// process to choose the most frequent recipient for any given gene transfer


	for (int i = 0; i < x; i++)
	{
		temprecipients.clear();
		int best = 0;

		int recsize = recipients[i].size();

		// if (array[0][i].isLeaf == true)
		// {
		// 	temprec.recnode = " ";
		// 	temprec.reccount = -1;
		// 	frequentrecipient.push_back(temprec);
		// }

		// else
		// {
			for(int j = 0; j< recsize; j++)
			{
				if(recipients[i][j].reccount > best)
				{
					best = recipients[i][j].reccount;
					temprec.recnode = recipients[i][j].recnode;
					temprec.reccount = recipients[i][j].reccount;
				}
			}

			frequentrecipient.push_back(temprec);

		// }

	}




	// calculate fraction of nodes with reliable events and mappings

	int totalnonleaf = 0;
	int goodevents = 0;
	int goodmappings = 0;
	int goodrecipients = 0;

	for (int i = 0; i < x; i++)
	{
		if (array[0][i].isLeaf == true)
		{

		}
		else
		{
			totalnonleaf++;

			if (((counts[i].spec * 100)/y) >= THRESHOLD)
			{
				goodevents++;
			}
			else if (((counts[i].dup * 100)/y) >= THRESHOLD)
			{
				goodevents++;
			}
			else if (((counts[i].tran * 100)/y) >= THRESHOLD)
			{
				goodevents++;
			}


			if (((frequentmapping[i].count * 100)/y) >= THRESHOLD)
			{
				goodmappings++;
			}
			if (((frequentrecipient[i].reccount * 100)/y) >= THRESHOLD)
			{
				goodrecipients++;
			}
		}
	}




// check if all files were full
if (FilesFullFlag == false)
		cout << "ERROR: Some reconciliation runs did not terminate correctly (" << FilesFullCount << " terminated correctly)" << endl;




	// output the aggregate information

	cout << endl << endl << "Aggregate reconciliation:" << endl;

//	cout << x <<  " " << y << endl;

	for (int i = 0; i < x; i++)
	{
		cout << array[0][i].genenode << ": ";
		if (array[0][i].isLeaf == true)
		{
			cout << "Leaf Node" << endl;
		}
		else
		{
			cout <<"[Speciations = " << counts[i].spec << ", Duplications = " << counts[i].dup << ", Transfers = " << counts[i].tran << "]";

			if (counts[i].tran > 0)
			{
				cout << ", [Most Frequent mapping --> " << frequentmapping[i].node << ", " << frequentmapping[i].count << " times]";
				cout << ", [Most Frequent recipient --> " << frequentrecipient[i].recnode << ", " << frequentrecipient[i].reccount << " times]." << endl;
			}
			else
			{
				cout << ", [Most Frequent mapping --> " << frequentmapping[i].node << ", " << frequentmapping[i].count << " times]." << endl;
			}

		}
	}

if (FilesFullFlag == true)
{
	cout << endl << endl << "Percentage of events with " << THRESHOLD << "% consistency = " << (((float)goodevents * 100)/(float)totalnonleaf) << endl;
	cout << "Percentage of mappings with " << THRESHOLD << "% consistency = " << (((float)goodmappings * 100)/(float)totalnonleaf) << endl;

	// cout << "Percentage of recipients with " << THRESHOLD << "% consistency = " << (((float)goodrecipients * 100)/(float)counts.tran) << endl;

	cout << "Total number of non-leaf nodes in gene tree: " << totalnonleaf << endl;
	cout << numsols << endl;
}

else
{
	cout << endl << endl << "Percentage of events with " << THRESHOLD << "% consistency = ERROR" << endl;
	cout << "Percentage of mappings with " << THRESHOLD << "% consistency = ERROR" << endl;

	// cout << "Percentage of recipients with " << THRESHOLD << "% consistency = ERROR" << endl;

	cout << "Total number of non-leaf nodes in gene tree: ERROR" << endl;
	cout << "Total number of optimal solutions: ERROR" << endl;
}

  return 0;
}
